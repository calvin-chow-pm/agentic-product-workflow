import json
import secrets
import threading
import urllib.error
import urllib.request
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .core import ROOT, digest, now, read, write


def make_server(demo, port=0):
    token = secrets.token_urlsafe(24)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, value, content_type="application/json", status=200):
            body = value.encode() if isinstance(value, str) else json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/":
                self.send((ROOT / "web/cover.html").read_text(), "text/html")
            elif path == "/workflow":
                self.send((ROOT / "web/workflow.html").read_text().replace("{{TOKEN}}", token), "text/html")
            elif path == "/api/state":
                self.send(demo.public())
            elif path == "/api/telemetry":
                file = demo.base / "telemetry.json"
                values = read(file) if file.exists() else []
                self.send({"events": values, "qa_events": sum(e["test"] for e in values), "note": "Local demonstration events, not historical customer behavior or measured CTA uplift."})
            elif path in {"/app", "/app/"}:
                self.send((demo.base / "application/index.html").read_text(), "text/html")
            elif path == "/baseline":
                self.send(demo.render(None, "Baseline · no contextual CTA"), "text/html")
            elif path in {"/production", "/production/"}:
                file = demo.base / "production.html"
                if not file.exists():
                    self.send({"status": "blocked", "reason": "Not released; human review and separate approval required"}, status=409)
                else:
                    self.send(file.read_text(), "text/html")
            elif path == "/walkthrough":
                file = ROOT / "recordings/walkthrough.html"
                if file.exists():
                    self.send(file.read_text(), "text/html")
                else:
                    self.send({"error": "Recording not exported yet"}, status=404)
            else:
                self.send({"error": "Route unavailable. No raw data or filesystem access exposed."}, status=404)

        def do_POST(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 8192:
                    raise ValueError("Invalid body size")
                body = json.loads(self.rfile.read(length))
                path = urlparse(self.path).path
                if path == "/api/telemetry":
                    if set(body) - {"event", "placement", "program", "test"}:
                        raise ValueError("Unsupported event data")
                    if body.get("event") not in {"analytics_cta_exposed", "analytics_cta_clicked", "dashboard_viewed", "dashboard_action"} or body.get("placement") not in {"overview", "within_item"}:
                        raise ValueError("Invalid telemetry event")
                    if not isinstance(body.get("test", False), bool):
                        raise ValueError("test must be boolean")
                    with demo.lock:
                        file = demo.base / "telemetry.json"
                        values = read(file) if file.exists() else []
                        values.append({"at": now(), **body, "test": body.get("test", False), "provenance": "local demonstration only"})
                        write(file, values)
                    self.send({"stored": True})
                    return
                if self.headers.get("X-Demo-Review") != token:
                    self.send({"error": "Review token required"}, status=403)
                    return
                if path == "/api/human-review":
                    result = demo.human_review(body.get("reviewer", ""), body.get("note", ""))
                elif path == "/api/approve-learning":
                    result = demo.approve_learning(body.get("id", ""), body.get("reviewer", ""))
                elif path == "/api/release":
                    result = demo.release()
                elif path == "/api/sync":
                    result = demo.sync()
                elif path == "/api/reuse":
                    result = demo.reuse()
                else:
                    self.send({"error": "Unknown action"}, status=404)
                    return
                self.send(result)
            except (ValueError, KeyError, FileNotFoundError) as exc:
                self.send({"error": str(exc)}, status=400)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(demo, port):
    server = make_server(demo, port)
    print("Local reconstruction: http://127.0.0.1:" + str(server.server_port), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))


def qa(demo, production=False):
    state = demo.state()
    if production and not state["released"]:
        raise ValueError("Production QA requires an actual local release")
    server = make_server(demo)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = "http://127.0.0.1:" + str(server.server_port)
    checks = []
    try:
        html = urllib.request.urlopen(base + ("/production" if production else "/app")).read().decode()
        parser = Links()
        parser.feed(html)
        links = [l for l in parser.links if l.get("data-event") == "analytics_cta_clicked"]
        checks.append({"name": "Exactly one contextual CTA at selected placement", "passed": len(links) == 1 and links[0].get("data-placement") == state["placement"]})
        if links:
            target = urllib.request.urlopen(base + ("/production/" if production else "/app/") + links[0]["href"]).read().decode()
            checks.append({"name": "Destination serves analytics view and useful dashboard action", "passed": 'id="analytics"' in target and 'id="report-action"' in target})
            checks.append({"name": "Overview does not impose a program filter; within-item preserves it", "passed": ("program=" not in links[0]["href"]) if state["placement"] == "overview" else ("program=first-aid" in links[0]["href"])})
        baseline = urllib.request.urlopen(base + "/baseline").read().decode()
        checks.append({"name": "Baseline has no contextual CTA", "passed": "data-event=\"analytics_cta_clicked\"" not in baseline})
        for route in ["/data/usage.csv", "/../data/usage.csv", "/api/raw-data"]:
            try:
                urllib.request.urlopen(base + route)
                passed = False
            except urllib.error.HTTPError as exc:
                passed = exc.code == 404
            checks.append({"name": "Raw dataset route denied: " + route, "passed": passed})
        payload = {"event": "analytics_cta_clicked", "placement": state["placement"], "program": None, "test": True}
        request = urllib.request.Request(base + "/api/telemetry", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        response = json.loads(urllib.request.urlopen(request).read())
        events = json.loads(urllib.request.urlopen(base + "/api/telemetry").read())
        checks.append({"name": "Event receiver stores QA-marked event separately from customer outcomes", "passed": response["stored"] and events["events"][-1]["test"]})
        checks.append({"name": "Demo sample-data and outcome disclosures remain visible", "passed": "All numbers are sample data" in html and "No measured CTA uplift" in html})
        if production:
            checks.append({"name": "Production artifact matches the reviewed release hash", "passed": digest(demo.base / "production.html") == state.get("released_sha256") == state["candidate_sha256"]})
        report = {"passed": all(c["passed"] for c in checks), "checks": checks, "sha256": digest(demo.base / ("production.html" if production else "application/index.html")), "at": now(), "scope": "Actual HTTP, HTML structure and event-receiver checks. No visual browser verification is claimed; these checks alone do not execute JavaScript.", "production": production}
        if not production:
            demo.update(qa=report)
        demo.event("production-qa" if production else "qa", "QA worker", "Production checks completed" if production else "Candidate checks completed", report)
        return report
    finally:
        server.shutdown()
        server.server_close()
        worker.join()
