import sys, os, json, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from nightshift import scout, vault
from nightshift.pipeline import run_pipeline, DEFAULT_CONFIG


class TestScout(unittest.TestCase):
    def test_thread_is_three_drafts(self):
        draft, posts = scout.render_thread_draft("RecoverLite", "goal", "headline")
        self.assertEqual(len(posts), 3)
        self.assertIn("DRAFT ONLY", draft)

    def test_no_signals_connected(self):
        self.assertFalse(scout.scan_signals(None)["connected"])

    def test_signals_keyword_counts(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("Stripe churn pain, stripe pricing pain")
            path = f.name
        try:
            r = scout.scan_signals(path)
            self.assertTrue(r["connected"])
            counts = {h["keyword"]: h["count"] for h in r["hits"]}
            self.assertEqual(counts["stripe"], 2)
            self.assertEqual(counts["pain"], 2)
        finally:
            os.unlink(path)


class TestPipeline(unittest.TestCase):
    def test_end_to_end(self):
        os.environ.pop("GEMINI_API_KEY", None)
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "run1")
            s = run_pipeline("为 RecoverLite 做一个落地页", out,
                             config=dict(DEFAULT_CONFIG), target_dir=d)
            self.assertEqual(s["total_cost"], 0.0)
            self.assertEqual(s["signups"], 0)
            self.assertEqual(s["product"], "RecoverLite")
            for rel in ["plan.json", "research.md", "decisions.json",
                        "build/index.html", "social_draft.md", "signals.json",
                        "cost_ledger.json", "report.html", "state.json", "night-shift.log"]:
                self.assertTrue(os.path.isfile(os.path.join(out, rel)), rel)
            with open(os.path.join(out, "report.html"), encoding="utf-8") as fh: report = fh.read()
            self.assertIn("not connected", report)
            self.assertIn("$0.00", report)
            with open(os.path.join(out, "build", "index.html"), encoding="utf-8") as fh: landing = fh.read()
            self.assertIn("RecoverLite", landing)
            with open(os.path.join(out, "cost_ledger.json")) as fh: ledger = json.load(fh)
            self.assertEqual(ledger["total_usd"], 0.0)
            vault_notes = os.listdir(os.path.join(out, "vault"))
            self.assertEqual(len(vault_notes), 1)
            with open(os.path.join(out, "vault", vault_notes[0]), encoding="utf-8") as fh: note = fh.read()
            self.assertIn("[[decider]]", note)
            # resume: second run reuses checkpoints, still succeeds
            s2 = run_pipeline("为 RecoverLite 做一个落地页", out,
                              config=dict(DEFAULT_CONFIG), target_dir=d)
            self.assertEqual(s2["product"], "RecoverLite")


if __name__ == "__main__":
    unittest.main()
