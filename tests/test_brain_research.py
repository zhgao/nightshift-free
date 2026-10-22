import sys, os, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from nightshift import brain, researcher


class TestBrain(unittest.TestCase):
    def setUp(self):
        os.environ.pop("GEMINI_API_KEY", None)

    def test_offline_without_key(self):
        r = brain.plan("为 RecoverLite 做一个落地页")
        self.assertEqual(r.mode, "offline-template")
        self.assertEqual(r.cost_usd, 0.0)
        self.assertEqual(r.plan["product_name"], "RecoverLite")

    def test_extract_product(self):
        self.assertEqual(brain.extract_product_name("Build a page for ClipPay"), "ClipPay")
        self.assertTrue(brain.extract_product_name(""))

    def test_plan_shape(self):
        p = brain.offline_plan("x goal")
        self.assertIn("steps", p)
        self.assertIn("features", p)


class TestResearcher(unittest.TestCase):
    def test_counts_and_todos(self):
        with tempfile.TemporaryDirectory() as d:
            for name, content in [("a.py", "# TODO fix me\nx=1\n"), ("README.md", "# Hello\nworld\n"), ("b.txt", "hi\n")]:
                with open(os.path.join(d, name), "w") as fh: fh.write(content)
            ev = researcher.analyze(d, "goal")
            self.assertEqual(ev["total_files"], 3)
            self.assertEqual(len(ev["todos"]), 1)
            self.assertIn("Hello", ev["readme_excerpt"])
            md = researcher.render_markdown(ev)
            self.assertIn("REA-lite", md)
            self.assertIn("Not full reverse engineering", md)

    def test_missing_dir_is_safe(self):
        ev = researcher.analyze("/nonexistent-dir-xyz", "")
        self.assertEqual(ev["total_files"], 0)


if __name__ == "__main__":
    unittest.main()
