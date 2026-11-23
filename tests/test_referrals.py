import json
import math
import unittest

from pipeline.build import ROOT
from pipeline.referrals import CHANNELS, FORMATS, PUBLISHERS, build_referrals, phi_coefficient


class AttributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_referrals()
        cls.trials = json.loads((ROOT / "data/experiment.json").read_text())["cases"]

    def test_endpoint_rebuilds(self):
        self.assertEqual(self.data, json.loads((ROOT / "data/referrals.json").read_text()))

    def test_all_sessions_and_outcomes_reconciled(self):
        for case_id, summary in self.data["cases"].items():
            with self.subTest(case_id=case_id):
                arms = [self.trials[case_id][name] for name in ("control", "treatment")]
                self.assertEqual([r["channel"] for r in summary["channels"]], list(CHANNELS))
                for k in ("n", "carts", "purchases"):
                    self.assertEqual(sum(row[k] for row in summary["channels"]), sum(arm[k] for arm in arms))
                ai, organic, direct, unknown = summary["channels"]
                self.assertEqual(summary["ambiguous_sessions"], direct["n"] + unknown["n"])
                self.assertAlmostEqual(summary["observed_gap_pp"], ai["cart_rate_pct"] - organic["cart_rate_pct"])

    def test_balanced_panel_reconciles_to_weeks_and_format(self):
        for case in self.data["cases"].values():
            sources, weekly = case["sources"], case["weekly"]
            self.assertEqual({(p, f) for p in PUBLISHERS for f in FORMATS},
                             {(r["publisher"], r["format"]) for r in sources})
            self.assertEqual([r["week"] for r in weekly], [1, 2, 3, 4])
            self.assertEqual(len({r["probes"] for r in sources}), 1)
            for k in ("probes", "cited"):
                self.assertEqual(sum(r[k] for r in sources), sum(r[k] for r in weekly))
            self.assertTrue(math.isclose(phi_coefficient(sources), case["format_correlation_r"], rel_tol=1e-8))

    def test_format_association_sign_and_unidentifiable(self):
        rows = [{"format": "Fact table", "probes": 3, "cited": 3},
                {"format": "Prose", "probes": 3, "cited": 0}]
        self.assertEqual(phi_coefficient(rows), 1.0)
        rows[1]["cited"] = 3
        self.assertIsNone(phi_coefficient(rows))


if __name__ == "__main__":
    unittest.main()
