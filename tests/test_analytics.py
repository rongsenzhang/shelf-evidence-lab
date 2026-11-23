from pathlib import Path
import json
import tempfile
import unittest

from pipeline.build import ARM_NAMES, COUNTS, ROOT, build, decide, difference, srm_p, wilson


class TrialEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build()

    def test_committed_endpoint_rebuilds(self):
        self.assertEqual(self.payload, json.loads((ROOT / "data/experiment.json").read_text()))

    def test_three_planned_decision_paths(self):
        cases = self.payload["cases"]
        self.assertEqual([cases[k]["decision"] for k in ("headphones", "monitor", "speaker")],
                         ["Advance to pilot", "Collect more evidence", "Hold for investigation"])
        self.assertLess(cases["speaker"]["balance_p"], 0.01)
        self.assertGreater(cases["speaker"]["ci_low_pp"], 0.5)
        self.assertEqual(decide(.009, 50)[0], "Hold for investigation")
        self.assertEqual(decide(1, .5)[0], "Collect more evidence")

    def test_counts_rates_and_partitions(self):
        for trial in self.payload["cases"].values():
            with self.subTest(case=trial["id"]):
                self.assertEqual(len(trial["daily"]), 28)
                self.assertEqual({g["device"] for g in trial["devices"]}, {"Mobile", "Desktop"})
                for arm in ARM_NAMES:
                    for key in COUNTS:
                        for records in (trial["daily"], trial["devices"]):
                            self.assertEqual(trial[arm][key], sum(row[arm][key] for row in records))
                    self.assertLessEqual(trial[arm]["purchases"], trial[arm]["carts"])
                    self.assertLessEqual(trial[arm]["carts"], trial[arm]["n"])
                    self.assertLessEqual(trial[arm]["engaged"], trial[arm]["n"])
                reference = 100 * (trial["treatment"]["carts"] / trial["treatment"]["n"]
                                   - trial["control"]["carts"] / trial["control"]["n"])
                self.assertAlmostEqual(trial["effect_pp"], reference)
                self.assertLess(trial["ci_low_pp"], reference)
                self.assertGreater(trial["ci_high_pp"], reference)
                self.assertLessEqual(trial["sensitivity"]["leave_one_day_out_min_pp"],
                                     trial["sensitivity"]["leave_one_day_out_max_pp"])

    def test_score_interval_and_srm_reference(self):
        # Wilson 95% CI for 5 successes in 10 observations.
        lo, hi = wilson(5, 10)
        self.assertAlmostEqual(lo, 0.236593090512564, places=10)
        self.assertAlmostEqual(hi, 0.763406909487436, places=10)
        self.assertEqual(srm_p(10, 10), 1.0)
        self.assertAlmostEqual(srm_p(60, 40), 0.0455002638963584)
        edge = difference({"control": {"n": 10, "carts": 0}, "treatment": {"n": 10, "carts": 0}})
        self.assertIsNone(edge["relative_lift_pct"])
        self.assertLess(edge["ci_low_pp"], 0)
        self.assertGreater(edge["ci_high_pp"], 0)

    def test_raw_export_includes_nonconverters(self):
        import csv
        with tempfile.TemporaryDirectory() as folder:
            csv_path = Path(folder) / "trial.csv"
            build(csv_path)
            with csv_path.open(newline="") as stream:
                raw = list(csv.DictReader(stream))
            expected = sum(c[arm]["n"] for c in self.payload["cases"].values() for arm in ARM_NAMES)
            self.assertEqual(expected, len(raw))
            self.assertEqual(len({r["session_id"] for r in raw}), expected)
            self.assertTrue(any(r["engaged"] == r["carts"] == r["purchases"] == "0" for r in raw))


if __name__ == "__main__":
    unittest.main()
