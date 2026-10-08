import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from demo.core import Capability, Demo, ROOT, read, write
from demo.server import qa


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.demo = Demo(Path(self.temp.name) / "run")
        self.demo.init()
        self.demo.analyze_usage()
        self.cap = Capability(self.demo)
        self.proposal = {"observations": ["Synthetic dashboard access is lower."], "hypotheses": ["Discoverability may matter."], "alternatives": ["Report value, permissions, timing."], "recommendation": "Test overview placement; no uplift claimed."}
        self.demo.submit("strategy", self.proposal, source="test-fixture")

    def tearDown(self):
        self.temp.cleanup()

    def prepare(self, placement="overview"):
        self.demo.request()
        self.demo.process_relay()
        self.demo.validate()
        self.demo.submit("design", self.proposal, source="test-fixture")
        self.demo.choose(placement, "Test fixture, not human approval", "test-fixture")
        self.demo.build()
        return qa(self.demo)

    def release_fixture(self):
        self.prepare()
        self.demo.human_review("Synthetic test human", "Test-only manual attestation")
        self.demo.reviewer_approve("Synthetic test reviewer", "Test-only separate attestation")
        self.demo.release()

    def test_initial_insight_has_matched_window_and_explicit_denominators(self):
        insight = read(self.demo.cloud / "initial-insight.json")
        self.assertEqual(insight["rows"][0]["access"], 0.22)
        self.assertEqual(insight["rows"][0]["engagement"], 0.14)
        self.assertEqual({r["period_days"] for r in insight["rows"]}, {28})
        self.assertLess(next(i for i,e in enumerate(self.demo.state()["events"]) if e["phase"] == "insight"), next(i for i,e in enumerate(self.demo.state()["events"]) if e["phase"] == "exploration"))

    def test_cloud_tools_cannot_read_raw_data_or_approve(self):
        for name,args in [("read_file", {"path": "data/usage.csv"}), ("release", {}), ("approve_learning", {}), ("read_workspace", {"path": "../authoritative/context.json"}), ("request_analysis", {"operation": "raw_sql"}), ("request_analysis", {"query": "SELECT *"})]:
            with self.subTest(name=name,args=args), self.assertRaises(ValueError):
                self.cap.call(name, args)

    def test_unknown_request_ids_and_path_traversal_rejected(self):
        for key in ["../x", "/tmp/x", "ABC", "", "x"*65]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.demo.request(key)

    def test_missing_response_remains_pending(self):
        self.demo.request()
        self.assertEqual(self.demo.observe()["status"], "pending")
        with self.assertRaises(ValueError):
            self.demo.validate()

    def test_relay_and_notification_idempotency(self):
        self.demo.request()
        self.assertEqual(self.demo.process_relay()["processed"], 1)
        before = self.demo.state()["events"]
        self.assertEqual(self.demo.process_relay()["processed"], 0)
        self.assertEqual(before, self.demo.state()["events"])
        self.demo.observe()
        self.demo.observe()
        self.assertEqual(sum(e["phase"] == "notification" for e in self.demo.state()["events"]), 1)

    def test_concurrent_workers_process_request_only_once(self):
        self.demo.request()
        processes = [subprocess.Popen([sys.executable, "-m", "demo", "--runtime", str(self.demo.base), "relay"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        values = []
        for proc in processes:
            out, err = proc.communicate(timeout=10)
            self.assertEqual(proc.returncode, 0, err)
            values.append(json.loads(out)["processed"])
        self.assertEqual(sorted(values), [0,1])

    def test_changed_request_is_rejected(self):
        self.demo.request()
        self.demo.process_relay()
        path = self.demo.cloud / "_outbox/placement-001.json"
        value = read(path)
        value["question"] = "Changed after completion"
        write(path, value)
        with self.assertRaises(ValueError):
            self.demo.process_relay()

    def test_validator_catches_seeded_denominator_error(self):
        self.demo.request()
        self.demo.process_relay()
        value = self.demo.validate()
        self.assertTrue(value["seeded_failure_detected"])
        self.assertEqual(value["corrected"]["overview"]["exposed_active_admins"], 155)
        self.assertEqual(value["corrected"]["overview"]["rate"], 0.4581)

    def test_invalid_link_populations_and_windows_rejected(self):
        self.demo.request()
        file = self.demo.truth / "data/link_usage.csv"
        original = file.read_text()
        for content in [original.replace("80,38,28", "80,81,28"), original.replace("80,38,28", "80,38,27")]:
            file.write_text(content)
            with self.assertRaises(ValueError):
                self.demo.process_relay()

    def test_provenance_cannot_be_overridden(self):
        for field in ["role", "source", "submitted_at"]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.demo.submit("strategy", {**self.proposal, field: "forged"})

    def test_qa_both_supported_placements(self):
        self.assertTrue(self.prepare()["passed"])
        self.demo.choose("within_item", "Test alternate", "test-fixture")
        self.demo.build()
        self.assertTrue(qa(self.demo)["passed"])

    def test_release_rejects_missing_failed_or_stale_checks(self):
        with self.assertRaises(ValueError):
            self.demo.release()
        self.prepare()
        with self.assertRaises(ValueError):
            self.demo.release()
        self.demo.human_review("Synthetic test human", "Test only")
        self.demo.reviewer_approve("Synthetic test reviewer", "Test only")
        file = self.demo.base / "application/index.html"
        file.write_text(file.read_text()+"\n<!-- changed -->")
        with self.assertRaises(ValueError):
            self.demo.release()

    def test_separate_reviewers_required(self):
        self.prepare()
        self.demo.human_review("Same name", "Test only")
        with self.assertRaises(ValueError):
            self.demo.reviewer_approve("Same name", "Test only")

    def test_real_git_release_and_production_hash_checked(self):
        self.release_fixture()
        self.assertEqual(self.demo.git("branch", "--show-current"), "main")
        self.assertTrue(qa(self.demo, production=True)["passed"])
        with self.assertRaises(ValueError):
            self.demo.choose("within_item", "Try changing released run")
        file = self.demo.base / "production.html"
        file.write_text(file.read_text()+"\n<!-- changed -->")
        self.assertFalse(qa(self.demo, production=True)["passed"])

    def test_pending_learning_excluded_and_reviewed_learning_reaches_prompt(self):
        lesson = self.demo.stage_learning("Unique approved guidance: use comparable exposed cohorts.")
        context = self.demo.sync()
        self.assertEqual(context["learnings"], [])
        with self.assertRaises(ValueError):
            self.demo.reuse()
        self.demo.approve_learning(lesson["id"], "Synthetic test human")
        context = self.demo.sync()
        self.assertEqual(context["version"], 2)
        result = self.demo.reuse()
        self.assertIn(lesson["lesson"], result["assembled_task_prompt"])
        self.assertEqual(self.demo.sync()["version"], 2)
        self.assertEqual(len(read(self.demo.truth / "context.json")["learnings"]), 1)

    def test_mcp_tools_exclude_generic_access_and_approvals(self):
        messages = [{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}, {"jsonrpc":"2.0","id":2,"method":"tools/list"}, {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"release","arguments":{}}}]
        result = subprocess.run([sys.executable,"-m","demo","--runtime",str(self.demo.base),"mcp"],cwd=ROOT,input="\n".join(json.dumps(m) for m in messages)+"\n",capture_output=True,text=True,check=True)
        replies = [json.loads(line) for line in result.stdout.splitlines()]
        names = {t["name"] for t in replies[1]["result"]["tools"]}
        self.assertEqual(names,{"read_workspace","request_analysis","check_inbox","submit_proposal","stage_learning"})
        self.assertTrue(replies[2]["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
