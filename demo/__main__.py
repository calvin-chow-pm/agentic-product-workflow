import argparse
import json
import sys
from pathlib import Path

from .core import Capability, Demo


def main():
    p = argparse.ArgumentParser(description="Runnable Analytics CTA reconstruction; synthetic data only")
    p.add_argument("--runtime", help="Separate run directory; default .runtime")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ["init", "discover", "relay", "validate", "build", "release", "sync", "reuse", "status", "export", "mcp"]:
        sub.add_parser(name)
    cap = sub.add_parser("tool")
    cap.add_argument("name")
    cap.add_argument("--args", default="{}", help="JSON tool arguments")
    cap.add_argument("--file", help="Read tool arguments from a JSON file")
    choose = sub.add_parser("choose")
    choose.add_argument("placement", choices=["overview", "within_item"])
    choose.add_argument("--rationale", required=True)
    choose.add_argument("--actor", default="Codex implementation default")
    for name in ["human-review", "reviewer-approve"]:
        cmd = sub.add_parser(name)
        cmd.add_argument("--reviewer", required=True)
        cmd.add_argument("--note", required=True)
    approve = sub.add_parser("approve-learning")
    approve.add_argument("id")
    approve.add_argument("--reviewer", required=True)
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8766)
    qa = sub.add_parser("qa")
    qa.add_argument("--production", action="store_true")
    record = sub.add_parser("record")
    record.add_argument("--output", default="recordings/walkthrough.html")
    args = p.parse_args()
    demo = Demo(args.runtime)
    if args.command == "init":
        result = demo.init()
    elif args.command == "tool":
        value = json.loads(Path(args.file).read_text()) if args.file else json.loads(args.args)
        result = Capability(demo).call(args.name, value)
    elif args.command == "discover":
        result = demo.analyze_usage()
    elif args.command == "relay":
        result = demo.process_relay()
    elif args.command == "validate":
        result = demo.validate()
    elif args.command == "choose":
        result = demo.choose(args.placement, args.rationale, args.actor)
    elif args.command == "build":
        result = demo.build()
    elif args.command == "human-review":
        result = demo.human_review(args.reviewer, args.note)
    elif args.command == "reviewer-approve":
        result = demo.reviewer_approve(args.reviewer, args.note)
    elif args.command == "release":
        result = demo.release()
    elif args.command == "approve-learning":
        result = demo.approve_learning(args.id, args.reviewer)
    elif args.command == "sync":
        result = demo.sync()
    elif args.command == "reuse":
        result = demo.reuse()
    elif args.command == "qa":
        from .server import qa
        result = qa(demo, args.production)
    elif args.command == "serve":
        from .server import serve
        serve(demo, args.port)
        return
    elif args.command == "record":
        from .record import record
        result = record(demo, Path(args.output))
    elif args.command == "mcp":
        from .mcp import serve_mcp
        serve_mcp(demo)
        return
    elif args.command == "export":
        target = Path("recordings/run.json")
        target.write_text(json.dumps(demo.public(), indent=2) + "\n")
        result = {"output": str(target), "contains": "Actual local run, synthetic evidence, explicit approval state"}
    else:
        result = demo.public()
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(1)
