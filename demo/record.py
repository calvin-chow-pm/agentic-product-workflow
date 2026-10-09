"""Export an immutable, paced walkthrough of actual execution evidence.

This is an edited evidence-log playback, not a browser screen recording or a
claim that recorded agent reasoning is being rerun during playback.
"""
import html
import json
from pathlib import Path

from .core import ROOT, digest, now, read, write


def chapters(demo):
    state = demo.public()
    def events(*phases):
        return [e for e in state["events"] if e["phase"] in phases]
    return [
        {"duration": 15, "title": "An insight started the work.", "subtitle": "A reconstruction of a workflow Calvin built and used at Thinkific.", "takeaway": "Codex reasoning and a real local relay. Synthetic inputs. Original company code excluded.", "evidence": {"execution": state["mode"], "created_at": state["created_at"], "historical_stack": "Claude / Confluence / Grok Bot / Drive / Cursor", "reconstruction_stack": "Codex / Python / local inbox-outbox / small web application"}, "events": events("ready")},
        {"duration": 30, "title": "Adoption was comparable. Usage wasn’t.", "subtitle": "The problem came before the placement question.", "takeaway": "Certification dashboard access: 22 / 100 active admins. Action reach: 14 / 100. All values are synthetic.", "evidence": state["initial-insight"], "events": events("insight")},
        {"duration": 30, "title": "Investigate before adding a link.", "subtitle": "Strategy and challenger contributions came from real Codex work.", "takeaway": "Discoverability, task timing, report value and permissions remain competing explanations.", "evidence": {"proposals": [p for p in state["proposals"] if p["role"] in {"strategy","challenger"}]}, "events": events("exploration")},
        {"duration": 30, "title": "Bring missing evidence across the boundary.", "subtitle": "Request → trusted analysis worker → response → notification.", "takeaway": "The scoped agent tools cannot query raw data. The worker returns aggregate placement evidence through the relay.", "evidence": {"relay_events": events("request","response","notification"), "pending_requests": state["pending_requests"]}, "events": events("request","response","notification")},
        {"duration": 30, "title": "A wrong denominator changed the story.", "subtitle": "A deliberately seeded demonstration failure, not a historical incident.", "takeaway": "29.6% used eligible admins. Corrected overview click-through is 45.8% of exposed admins, versus 28.0% within-item. Association is not causation.", "evidence": {"validation": state["validation"], "placement": state["placement"], "rationale": state.get("rationale"), "design": [p for p in state["proposals"] if p["role"]=="design"]}, "events": events("validation","decision")},
        {"duration": 35, "title": "Build a working improvement.", "subtitle": "A contextual analytics link beside the program-list heading.", "takeaway": "The link opens all-program analytics. HTTP, telemetry and JavaScript unit checks validate behavior; visual browser verification is unavailable.", "evidence": {"candidate_commit": state.get("candidate_commit"), "qa": state.get("qa"), "artifact": "Captured candidate application HTML is embedded in the playback; not a screenshot."}, "events": events("build","qa")},
        {"duration": 20, "title": "Release follows real review.", "subtitle": "No human or historical EM approval is fabricated.", "takeaway": "Release locally after manual review and separate approval of the exact tested change. Measure useful activity; the synthetic reconstruction does not measure customer uplift. Historical outcomes are documented separately.", "evidence": {"released": state["released"], "human_review": state["human_review"], "separate_reviewer": state["reviewer"], "production_qa": events("production-qa")}, "events": events("approval","release","production-qa")},
        {"duration": 20, "title": "The learning returns to shared context.", "subtitle": "Review → source of truth → context pack → next task.", "takeaway": "Pending learnings are excluded. Approved lessons enter the next task prompt; the actual recorded state is shown below.", "evidence": {"context_pack": state["context_pack"], "subsequent_task": state["subsequent-task"], "learning_events": events("learning","learning-approval","sync","reuse")}, "events": events("learning","learning-approval","sync","reuse")},
    ]


def record(demo, output):
    state = demo.public()
    values = chapters(demo)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    prior_manifest = read(output.parent / "manifest.json") if (output.parent / "manifest.json").exists() else {}
    write(output.parent / "run.json", state)
    write(output.parent / "chapters.json", values)
    candidate = (demo.base / "application/index.html").read_text()
    baseline = demo.render(None, "Captured baseline")
    payload = json.dumps({"chapters": values, "run": state, "candidate": candidate, "baseline": baseline}, ensure_ascii=False).replace("<", "\\u003c")
    template = (ROOT / "web/playback.html").read_text()
    output.write_text(template.replace("{{PAYLOAD}}", payload))
    manifest = {"exported_at": now(), "duration_seconds": sum(c["duration"] for c in values), "format": "Edited evidence-log playback; not a browser screen recording", "agent_reasoning": "Captured real Codex contributions; playback performs no new inference", "human_review": state["human_review"], "released": state["released"], "candidate_sha256": digest(demo.base / "application/index.html"), "run_sha256": digest(output.parent / "run.json"), "playback_sha256": digest(output), "browser_verification": "Unavailable: security-policy check blocked browser automation", "inputs": "Synthetic only"}
    if prior_manifest.get("video"):
        manifest["video"] = prior_manifest["video"]
        manifest["video"]["snapshot_current"] = manifest["video"].get("source_run_sha256") == manifest["run_sha256"]
    write(output.parent / "manifest.json", manifest)
    return {"output": str(output.resolve()), **manifest}
