from __future__ import annotations

import csv
import fcntl
import functools
import hashlib
import json
import re
import shutil
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABEL = "Reconstructed from a workflow I built and used at Thinkific. Uses synthetic data and a demonstration application; original company code is excluded."
ROLES = {"strategy", "challenger", "design", "engineering", "qa"}


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temp.replace(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Demo:
    """Trusted controller. Only Capability exposes tools to the agent workspace.

    The dataset is deliberately synthetic. This is a tool boundary, not isolation
    from a malicious local user or the trusted Codex authoring session.
    """

    def __init__(self, runtime=None):
        self.base = Path(runtime or ROOT / ".runtime").resolve()
        self.cloud = self.base / "cloud"
        self.truth = self.base / "authoritative"
        self.lock = threading.RLock()
        self._depth = 0

    def init(self):
        if (self.base / "state.json").exists() and (self.base / "application/.git").exists():
            return self.state()
        self.base.mkdir(parents=True, exist_ok=True)
        for folder in [self.cloud / "_outbox", self.cloud / "_inbox", self.cloud / "proposals", self.cloud / "learnings", self.truth, self.base / "application"]:
            folder.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT / "data", self.truth / "data", dirs_exist_ok=True)
        write(self.truth / "context.json", {"version": 1, "preferences": ["Start from the customer problem.", "Distinguish observations, hypotheses, decisions, and measured outcomes.", "Challenge a recommendation with an alternative.", "Require explicit human approval for release and new learnings."], "learnings": [], "historical_note": "Claude held the source of truth; Confluence held the Grok Bot context pack. Weekly refresh ran both ways. The Drive inbox/outbox handled on-demand deep-data requests."})
        write(self.cloud / "context-pack.json", read(self.truth / "context.json"))
        write(self.cloud / "feedback.json", read(self.truth / "data/feedback.json"))
        write(self.base / "state.json", {"label": LABEL, "mode": "actual local execution / synthetic inputs", "created_at": now(), "phase": "ready", "placement": None, "human_review": None, "reviewer": None, "released": False, "qa": None, "events": [], "learnings": {}, "pending": []})
        app = self.base / "application"
        (app / "index.html").write_text(self.render(None, "Baseline"))
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Demo reconstruction")
        self.git("config", "user.email", "demo@example.invalid")
        self.git("add", "index.html")
        self.git("commit", "-m", "Baseline certification workspace (synthetic)")
        self.event("ready", "controller", "Reconstruction initialized", {"synthetic": True, "human_approvals": "Not yet supplied; never simulated in this run."})
        return self.state()

    def git(self, *args):
        proc = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", *args], cwd=self.base / "application", capture_output=True, text=True)
        if proc.returncode:
            raise ValueError(proc.stderr.strip())
        return proc.stdout.strip()

    def state(self):
        return read(self.base / "state.json")

    def event(self, phase, actor, title, evidence):
        with self.lock:
            state = self.state()
            entry = {"id": len(state["events"]) + 1, "at": now(), "phase": phase, "actor": actor, "title": title, "evidence": evidence}
            state["events"].append(entry)
            state["phase"] = phase
            write(self.base / "state.json", state)
            return entry

    def update(self, **values):
        state = self.state()
        state.update(values)
        write(self.base / "state.json", state)

    def analyze_usage(self):
        source = self.truth / "data/usage.csv"
        with source.open() as handle:
            rows = list(csv.DictReader(handle))
        results = []
        for row in rows:
            r = {k: (v if k == "product" else int(v)) for k, v in row.items()}
            if not 0 <= r["dashboard_actions"] <= r["dashboard_visitors"] <= r["active_product_admins"] <= r["eligible_admins"]:
                raise ValueError("Invalid synthetic usage population")
            r.update(adoption=round(r["active_product_admins"] / r["eligible_admins"], 4), access=round(r["dashboard_visitors"] / r["active_product_admins"], 4), engagement=round(r["dashboard_actions"] / r["active_product_admins"], 4))
            results.append(r)
        if len({r["period_days"] for r in results}) != 1:
            raise ValueError("Usage windows must match")
        report = {"source": "synthetic usage.csv", "source_sha256": digest(source), "rows": results, "definitions": {"adoption": "Unique active product admins / eligible admins", "access": "Unique dashboard visitors / active product admins", "engagement": "Unique admins taking at least one dashboard action / active product admins", "window": "Same 28-day window; matched synthetic admin populations. Each row is a distinct product cohort, not randomized treatment."}, "observation": "Certification adoption is comparable, but dashboard access and meaningful usage are lower.", "hypothesis": "A link at the right workflow step may improve discovery. The data does not prove the cause or the effect of a CTA.", "claim_boundary": "All values are synthetic. No historical dashboard-access or CTA-uplift metrics are asserted."}
        write(self.cloud / "initial-insight.json", report)
        self.event("insight", "authoritative-analysis-worker", "Usage insight precedes the placement question", report)
        return report

    def submit(self, role, value, source="codex-session"):
        if role not in ROLES:
            raise ValueError("Unknown role")
        if not isinstance(value, dict) or set(value) & {"role", "source", "submitted_at"}:
            raise ValueError("Proposal cannot override controller provenance")
        required = {"observations", "hypotheses", "alternatives", "recommendation"}
        if not required <= value.keys() or not all(isinstance(value[k], (str, list)) for k in required):
            raise ValueError("Proposal needs observations, hypotheses, alternatives, recommendation")
        if not (self.cloud / "initial-insight.json").exists():
            raise ValueError("Discover the problem before proposing placement")
        record = {"role": role, "source": source, "submitted_at": now(), **value}
        write(self.cloud / "proposals" / (role + ".json"), record)
        self.event("exploration", role, role.title() + " contribution captured", record)
        return record

    def request(self, request_id="placement-001", operation="link_usage"):
        if not re.fullmatch(r"[a-z0-9-]{1,64}", request_id):
            raise ValueError("Invalid request id")
        if operation != "link_usage":
            raise ValueError("Only aggregate link_usage is exposed; raw data and arbitrary queries are unavailable")
        if not (self.cloud / "proposals/strategy.json").exists():
            raise ValueError("Investigate the insight before requesting placement evidence")
        path = self.cloud / "_outbox" / (request_id + ".json")
        if path.exists():
            old = read(path)
            if old["operation"] != operation:
                raise ValueError("Request id conflict")
            return old
        req = {"id": request_id, "operation": operation, "requested_at": now(), "question": "How do contextual dashboard links perform on overview versus within-item pages in other product areas?", "status": "pending", "provenance": "Reconstruction request; fixed aggregate operation."}
        write(path, req)
        self.event("request", "strategy", "Missing evidence requested through _outbox", req)
        return req

    def process_relay(self):
        processed = []
        for path in sorted((self.cloud / "_outbox").glob("*.json")):
            req = read(path)
            request_id = req.get("id", "")
            if not re.fullmatch(r"[a-z0-9-]{1,64}", request_id) or request_id != path.stem or req.get("operation") != "link_usage":
                raise ValueError("Relay rejected an unsupported request")
            result = self.cloud / "_inbox" / (request_id + ".json")
            if result.exists():
                if read(result)["request_sha256"] != digest(path):
                    raise ValueError("Request changed after completion")
                continue
            source = self.truth / "data/link_usage.csv"
            with source.open() as handle:
                rows = [{k: v if k in {"product", "placement"} else int(v) for k, v in row.items()} for row in csv.DictReader(handle)]
            if not rows or len({r["period_days"] for r in rows}) != 1 or rows[0]["period_days"] <= 0:
                raise ValueError("Link-usage windows must match and be positive")
            if any(not 0 <= r["unique_clickers"] <= r["exposed_active_admins"] or r["exposed_active_admins"] <= 0 or r["placement"] not in {"overview", "within_item"} for r in rows):
                raise ValueError("Invalid link-usage population")
            aggregates = []
            for placement in ["overview", "within_item"]:
                subset = [r for r in rows if r["placement"] == placement]
                numerator = sum(r["unique_clickers"] for r in subset)
                denominator = sum(r["exposed_active_admins"] for r in subset)
                if denominator <= 0 or not 0 <= numerator <= denominator:
                    raise ValueError("Invalid link cohort")
                aggregates.append({"placement": placement, "unique_clickers": numerator, "exposed_active_admins": denominator, "rate": round(numerator / denominator, 4)})
            report = {"id": request_id, "request_sha256": digest(path), "completed_at": now(), "source": "synthetic link_usage.csv", "source_sha256": digest(source), "window_days": rows[0]["period_days"], "rows": rows, "aggregates": aggregates, "population": "Distinct product cohorts; pooled numerator and exposure denominator. Admins are unique within each row. Not a randomized placement experiment.", "seeded_failure": {"label": "Deliberately seeded demonstration failure, not a historical incident", "claim": "Overview links: 29.6%; within-item links: 28.0% — little difference.", "overview_denominator": "240 eligible admins (wrong population)", "within_item_denominator": "175 exposed active admins", "reported_overview_rate": round(71 / 240, 4), "reported_within_item_rate": 0.28}, "limitation": "Cross-product associations inform a hypothesis; placement, audience, and workflow differences may explain results."}
            write(result, report)
            processed.append(report)
            self.event("response", "authoritative-analysis-worker", "Analysis returned through _inbox", report)
        return {"processed": len(processed), "responses": processed}

    def observe(self, request_id="placement-001"):
        if not re.fullmatch(r"[a-z0-9-]{1,64}", request_id):
            raise ValueError("Invalid request id")
        path = self.cloud / "_inbox" / (request_id + ".json")
        if not path.exists():
            return {"id": request_id, "status": "pending", "message": "No response yet. Do not invent analysis."}
        report = read(path)
        state = self.state()
        if not any(e["phase"] == "notification" and e["evidence"].get("id") == request_id for e in state["events"]):
            self.event("notification", "data-agent", "Group notified: requested analysis has arrived", {"id": request_id, "response_source": report["source"], "status": "arrived"})
        return report

    def validate(self, request_id="placement-001"):
        report = self.observe(request_id)
        if report.get("status") == "pending":
            raise ValueError("Analysis still pending")
        correct = {r["placement"]: r for r in report["aggregates"]}
        seeded = report["seeded_failure"]
        detected = abs(seeded["reported_overview_rate"] - correct["overview"]["rate"]) > 0.001
        value = {"seeded_failure_detected": detected, "reason": "Overview used eligible admins while within-item used exposed active admins. Compare like denominators.", "corrected": correct, "reconsideration": "Overview remains a useful candidate, not a proven winner: selection and context differ. Combine with workflow evidence, then measure the shipped CTA.", "synthetic": True}
        if not detected:
            raise ValueError("Seeded error was not detected")
        write(self.cloud / "validation.json", value)
        self.event("validation", "validator", "Mismatched denominators detected and corrected", value)
        return value

    def choose(self, placement, rationale, actor="Codex implementation default"):
        if self.state()["released"]:
            raise ValueError("Released run is immutable; start a fresh run to change placement")
        if placement not in {"overview", "within_item"}:
            raise ValueError("Invalid placement")
        if not (self.cloud / "validation.json").exists() or not (self.cloud / "proposals/design.json").exists():
            raise ValueError("Need validated analysis and design exploration first")
        self.update(placement=placement, rationale=rationale, human_review=None, reviewer=None, qa=None)
        self.event("decision", actor, "Candidate placement selected; human review remains pending", {"placement": placement, "rationale": rationale, "approval": "This is an implementation choice, not Calvin's historical decision or manual approval."})
        return self.state()

    def render(self, placement, variant):
        template = (ROOT / "web/dashboard.html").read_text()
        cta = '<a class="analytics-cta" href="?view=analytics" data-event="analytics_cta_clicked" data-placement="overview">View certification analytics <span aria-hidden="true">↗</span></a>' if placement == "overview" else ""
        program_cta = '<a class="program-cta" href="?view=analytics&amp;program=first-aid" data-event="analytics_cta_clicked" data-placement="within_item">View program analytics ↗</a>' if placement == "within_item" else ""
        columns = ["program", "course", "actions"] if placement is None else ["select", "program", "course", "status", "template", "tags", "actions"]
        names = {"select": '<input id="select-all" type="checkbox" aria-label="Select all programs">', "program": "Program", "course": "Course", "status": "Status", "template": "Certificate template", "tags": "Tags", "actions": '<span class="sr-only">Actions</span>'}
        table_columns = "".join('<col class="col-' + key + '">' for key in columns)
        table_headings = "".join(('<th class="selection-cell">' if key == "select" else "<th>") + names[key] + "</th>" for key in columns)
        return template.replace("{{CTA}}", cta).replace("{{PROGRAM_CTA}}", program_cta).replace("{{VARIANT}}", variant).replace("{{TABLE_VARIANT}}", "baseline" if placement is None else "candidate").replace("{{TABLE_COLUMNS}}", table_columns).replace("{{TABLE_HEADINGS}}", table_headings)

    def build(self):
        state = self.state()
        if state["released"]:
            raise ValueError("This example has already been released; start a fresh run to rebuild")
        if not state["placement"]:
            raise ValueError("Choose placement first")
        app = self.base / "application"
        branch = self.git("branch", "--show-current")
        if branch == "main":
            self.git("checkout", "-b", "feature/analytics-cta")
        html = self.render(state["placement"], "Candidate · review pending")
        (app / "index.html").write_text(html)
        self.git("add", "index.html")
        if self.git("diff", "--cached", "--name-only"):
            self.git("commit", "-m", "Add contextual analytics CTA to synthetic workspace")
        commit = self.git("rev-parse", "HEAD")
        self.update(candidate_commit=commit, candidate_sha256=digest(app / "index.html"), qa=None, human_review=None, reviewer=None)
        self.event("build", "Codex engineering", "Working CTA implemented on a local feature branch", {"placement": state["placement"], "commit": commit, "sha256": digest(app / "index.html"), "method": "Actual generated application and Git commit; no Cursor or historical code execution claimed."})
        return {"commit": commit}

    def human_review(self, reviewer, note):
        if not reviewer.strip() or not note.strip():
            raise ValueError("Supply the human reviewer's name and review notes")
        state = self.state()
        self.require_fresh_qa(state)
        record = {"reviewer": reviewer, "note": note, "sha256": state["candidate_sha256"], "at": now(), "type": "local human attestation; identity is not authenticated"}
        self.update(human_review=record)
        self.event("approval", reviewer, "Manual review recorded", record)
        return record

    def reviewer_approve(self, reviewer, note):
        state = self.state()
        self.require_fresh_qa(state)
        if not reviewer.strip() or not note.strip():
            raise ValueError("Reviewer name and notes required")
        if state.get("human_review") and reviewer == state["human_review"]["reviewer"]:
            raise ValueError("Separate reviewer required")
        record = {"reviewer": reviewer, "note": note, "sha256": state["candidate_sha256"], "at": now(), "type": "separate review; may be a disclosed Codex reviewer, not a fictional EM"}
        self.update(reviewer=record)
        self.event("approval", reviewer, "Separate review recorded", record)
        return record

    def require_fresh_qa(self, state):
        current = digest(self.base / "application/index.html")
        if not state.get("qa") or not state["qa"]["passed"] or state["qa"]["sha256"] != current or state["candidate_sha256"] != current:
            raise ValueError("Passing QA for the current candidate required")
        if self.git("rev-parse", "HEAD") != state["candidate_commit"] or self.git("status", "--porcelain"):
            raise ValueError("Candidate commit changed or working tree is dirty")

    def release(self):
        state = self.state()
        if state["released"]:
            return {"status": "already released"}
        self.require_fresh_qa(state)
        for key in ["human_review", "reviewer"]:
            if not state[key] or state[key]["sha256"] != state["candidate_sha256"]:
                raise ValueError("Release blocked: manual review and separate reviewer approval required")
        if state["human_review"]["reviewer"] == state["reviewer"]["reviewer"]:
            raise ValueError("Separate reviewer required")
        self.git("checkout", "main")
        self.git("merge", "--no-ff", "feature/analytics-cta", "-m", "Release reviewed analytics CTA reconstruction")
        shutil.copy(self.base / "application/index.html", self.base / "production.html")
        self.update(released=True, released_sha256=digest(self.base / "production.html"))
        self.event("release", "trusted-controller", "Reviewed change merged and released locally", {"commit": self.git("rev-parse", "HEAD"), "destination": "Local demo only; nothing published", "measurement": "Measure CTA exposure → unique clicks → dashboard action. Segment by workflow and active admins; preserve 28-day windows. QA events are excluded. No uplift established."})
        return {"status": "released locally"}

    def stage_learning(self, lesson):
        if not lesson.strip() or len(lesson) > 2000:
            raise ValueError("Learning must be 1–2000 characters")
        key = hashlib.sha256(lesson.encode()).hexdigest()[:12]
        path = self.cloud / "learnings" / (key + ".json")
        if path.exists():
            return read(path)
        record = {"id": key, "lesson": lesson, "status": "pending", "provenance": "Proposed lesson from synthetic reconstruction; not a durable career correction."}
        write(path, record)
        self.event("learning", "agent-workspace", "Proposed learning staged outside authoritative context", record)
        return record

    def approve_learning(self, key, reviewer):
        if not re.fullmatch(r"[a-f0-9]{12}", key) or not reviewer.strip():
            raise ValueError("Valid learning id and reviewer required")
        path = self.cloud / "learnings" / (key + ".json")
        record = read(path)
        record.update(status="approved", approved_by=reviewer, approved_at=now())
        write(path, record)
        self.event("learning-approval", reviewer, "Learning approved for next context refresh", record)
        return record

    def sync(self):
        context = read(self.truth / "context.json")
        known = {r["id"] for r in context["learnings"]}
        added = []
        for path in sorted((self.cloud / "learnings").glob("*.json")):
            record = read(path)
            if record["status"] == "approved" and record["id"] not in known:
                context["learnings"].append(record)
                known.add(record["id"])
                added.append(record["id"])
        if added:
            context["version"] += 1
            write(self.truth / "context.json", context)
        write(self.cloud / "context-pack.json", context)
        self.event("sync", "context-refresh-worker", "Two-way context refresh completed", {"version": context["version"], "cloud_to_truth": added, "truth_to_cloud": "Authoritative preferences and approved learnings exported", "excluded_pending": [read(p)["id"] for p in (self.cloud / "learnings").glob("*.json") if read(p)["status"] != "approved"], "schedule": "Explicit reconstruction command; historical refresh was automatic weekly. No scheduler installed."})
        return context

    def reuse(self):
        context = read(self.cloud / "context-pack.json")
        if not context["learnings"]:
            raise ValueError("No approved learning has reached the context pack yet")
        instructions = [r["lesson"] for r in context["learnings"]]
        value = {"next_task": "Evaluate a contextual export link in the community workflow", "context_version": context["version"], "applied_learning_ids": [r["id"] for r in context["learnings"]], "required_analysis": instructions, "assembled_task_prompt": "Evaluate a contextual export link in the community workflow. Apply these reviewed lessons:\n" + "\n".join("- " + item for item in instructions), "scope": "Actual prompt assembly from refreshed context. The subsequent task's reasoning is not automatically run or claimed."}
        write(self.cloud / "subsequent-task.json", value)
        self.event("reuse", "strategy", "Subsequent task consumes refreshed context", value)
        return value

    def public(self):
        state = self.state()
        for name in ["initial-insight", "validation", "subsequent-task"]:
            path = self.cloud / (name + ".json")
            state[name] = read(path) if path.exists() else None
        state["proposals"] = [read(p) for p in sorted((self.cloud / "proposals").glob("*.json"))]
        state["pending_requests"] = [p.stem for p in (self.cloud / "_outbox").glob("*.json") if not (self.cloud / "_inbox" / p.name).exists()]
        state["context_pack"] = read(self.cloud / "context-pack.json")
        return state


def synchronized(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with self.lock:
            self.base.mkdir(parents=True, exist_ok=True)
            handle = None
            if self._depth == 0:
                handle = (self.base / ".run.lock").open("a")
                fcntl.flock(handle, fcntl.LOCK_EX)
            self._depth += 1
            try:
                return method(self, *args, **kwargs)
            finally:
                self._depth -= 1
                if handle:
                    fcntl.flock(handle, fcntl.LOCK_UN)
                    handle.close()
    return wrapper


for _name in ["init", "event", "update", "analyze_usage", "submit", "request", "process_relay", "observe", "validate", "choose", "build", "human_review", "reviewer_approve", "release", "stage_learning", "approve_learning", "sync", "reuse", "public"]:
    setattr(Demo, _name, synchronized(getattr(Demo, _name)))


class Capability:
    """The entire cloud-agent tool surface: no file path, shell, raw query, or approval tool."""

    def __init__(self, demo):
        self.demo = demo

    def call(self, name, args):
        allowed = {"read_workspace", "request_analysis", "check_inbox", "submit_proposal", "stage_learning"}
        if name not in allowed:
            raise ValueError("Tool unavailable to cloud agents")
        if name == "read_workspace":
            if args:
                raise ValueError("read_workspace accepts no paths or queries")
            public = self.demo.public()
            return {k: public[k] for k in ["initial-insight", "validation", "proposals", "pending_requests", "context_pack"]} | {"feedback": read(self.demo.cloud / "feedback.json")}
        if name == "request_analysis":
            if set(args) - {"request_id", "operation"}:
                raise ValueError("Unsupported analysis parameter")
            return self.demo.request(**args)
        if name == "check_inbox":
            if set(args) - {"request_id"}:
                raise ValueError("Unsupported inbox parameter")
            return self.demo.observe(**args)
        if name == "submit_proposal":
            if set(args) != {"role", "value"}:
                raise ValueError("Supply role and value")
            return self.demo.submit(**args)
        if name == "stage_learning":
            if set(args) != {"lesson"}:
                raise ValueError("Supply lesson")
            return self.demo.stage_learning(**args)
