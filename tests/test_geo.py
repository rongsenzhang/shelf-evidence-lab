import json
from collections import Counter
from pathlib import Path
import unittest

from pipeline import geo


class GeoAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = geo.build()

    def test_published_data_matches_rebuild(self):
        path = Path(__file__).resolve().parents[1] / "data" / "geo.json"
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), self.snapshot)

    def test_same_questions_and_replications_on_both_versions(self):
        for case in self.snapshot["cases"].values():
            questions = {q["id"] for q in case["questions"]}
            self.assertEqual(len(questions), 4)
            actual = Counter((r["question_id"], r["version"], r["repeat"]) for r in case["records"])
            expected = Counter((q, v, n) for q in questions for v in ("A", "B") for n in (1, 2))
            self.assertEqual(actual, expected)

    def test_cited_excerpt_must_reference_current_version_and_answer_fact(self):
        for case in self.snapshot["cases"].values():
            questions = {q["id"]: q for q in case["questions"]}
            for row in case["records"]:
                version = row["version"]
                passages = {p["id"]: p["text"] for p in case["versions"][version]["passages"]}
                quote = row["citation_quote"]
                is_valid = bool(quote and quote in passages.get(row["citation_id"], ""))
                self.assertEqual(row["citation_valid"], is_valid)
                question = questions[row["question_id"]]
                evidence = question["evidence"][version]
                is_supported = bool(is_valid and row["answer"] == question["truth"] and evidence
                                    and evidence["passage_id"] == row["citation_id"]
                                    and evidence["quote"] in quote)
                self.assertEqual(row["supported"], is_supported)

    def test_metrics_keep_abstentions_in_denominator(self):
        for case in self.snapshot["cases"].values():
            for v, counts in case["metrics"].items():
                self.assertEqual(counts["total"], 8)
                self.assertEqual(counts["total"], sum(counts[k] for k in ("correct", "incorrect", "abstain")))
                for field, flag in (("citation_rate", "citation_id"), ("support_rate", "supported"),
                                    ("valid_citation_rate", "citation_valid")):
                    self.assertEqual(counts[field], sum(bool(r[flag]) for r in case["records"] if r["version"] == v) / 8)
                self.assertEqual(counts["accuracy"], counts["correct"] / 8)

    def test_fixtures_expose_failure_modes(self):
        rows = [r for c in self.snapshot["cases"].values() for r in c["records"]]
        self.assertTrue(any(r["citation_id"] and not r["citation_valid"] for r in rows))
        self.assertTrue(any(r["citation_valid"] and r["verdict"] == "incorrect" for r in rows))
        self.assertTrue(any(r["citation_valid"] and r["verdict"] == "correct" and not r["supported"] for r in rows))
        self.assertTrue(any(not r["citation_id"] and r["verdict"] == "correct" for r in rows))
        self.assertTrue(any(r["verdict"] == "abstain" for r in rows))


if __name__ == "__main__":
    unittest.main()
