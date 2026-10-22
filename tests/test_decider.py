import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from nightshift import decider


class TestDecider(unittest.TestCase):
    def test_budget_gate_rejects_over_cap(self):
        d = decider.decide_budget("domain", 49.0, 10.0)
        self.assertFalse(d.approved)
        self.assertEqual(d.answer, "no")

    def test_budget_gate_allows_under_cap(self):
        self.assertTrue(decider.decide_budget("domain", 3.0, 10.0).approved)

    def test_domain_poster_scenario(self):
        # $49 wanted > $10 limit -> pick $3 cheap domain (draft only)
        d = decider.decide_domain(10.0)
        self.assertEqual(d.answer, "cheap domain")

    def test_domain_zero_cap_picks_free(self):
        d = decider.decide_domain(0.0)
        self.assertEqual(d.answer, "GitHub Pages / free subdomain")

    def test_domain_high_cap_picks_custom(self):
        self.assertEqual(decider.decide_domain(100.0).answer, "custom .com domain")

    def test_social_never_auto_posts(self):
        d = decider.decide_social_draft()
        self.assertFalse(d.approved)
        self.assertEqual(d.answer, "no")

    def test_decisions_are_typed(self):
        ds = decider.run_all_decisions("goal here", "Prod", 10.0, 49.0)
        self.assertTrue(all(d.kind in ("Choice", "Score", "YesNo") for d in ds))
        self.assertTrue(all(0.0 <= d.confidence <= 1.0 for d in ds))


if __name__ == "__main__":
    unittest.main()
