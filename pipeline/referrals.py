"""Build descriptive referral attribution and a separate synthetic citation panel."""
from collections import defaultdict
from datetime import date
import argparse
import json
import math
from pathlib import Path
import random
import sqlite3

if __package__:
    from .build import ROOT, START, SCENARIOS, make_rows, stable_precision
else:
    from build import ROOT, START, SCENARIOS, make_rows, stable_precision

CHANNELS = ("Tagged AI", "Organic search", "Direct / untagged", "Unknown / missing")
PUBLISHERS = ("Brand", "Retailer", "Editorial")
FORMATS = ("Fact table", "Prose")


def assigned_channel(rng, device, week):
    # Set the acquisition mix before consulting any shopping outcome.
    ai = 0.045 + 0.015 * week + 0.055 * (device == "Desktop")
    organic = 0.35 + 0.06 * (device == "Mobile")
    unknown = 0.13 + 0.04 * (device == "Mobile")
    draw = rng.random()
    if draw < ai:
        return CHANNELS[0]
    if draw < ai + organic:
        return CHANNELS[1]
    if draw < 1 - unknown:
        return CHANNELS[2]
    return CHANNELS[3]


def add_referrals(db, case_id, scenario):
    rng = random.Random(scenario["seed"] + 8000)
    def visits():
        for session, day, _, _, _, device, _, _, carts, purchases in make_rows(case_id, scenario):
            week = (date.fromisoformat(day) - START).days // 7 + 1
            yield session, case_id, assigned_channel(rng, device, week), week, carts, purchases
    db.executemany("INSERT INTO referrals VALUES (?, ?, ?, ?, ?, ?)", visits())


def add_probes(db, case_id, scenario, question_ids):
    # A separately authored simulator, independent of tagged traffic and trial variants.
    # Balanced design. Bernoulli outcomes are pedagogical, not retrieved citations.
    rng = random.Random(scenario["seed"] + 16000)
    rows = []
    for week in range(1, 5):
        for question in question_ids:
            for publisher, intercept in zip(PUBLISHERS, (0.34, 0.22, 0.43)):
                for fmt in FORMATS:
                    for repeat in range(1, 5):
                        probability = intercept + 0.035 * (week - 1) + 0.12 * (fmt == "Fact table")
                        cited = int(rng.random() < probability)
                        rows.append((case_id, week, question, publisher, fmt, repeat, cited))
    db.executemany("INSERT INTO probes VALUES (?, ?, ?, ?, ?, ?, ?)", rows)


def grouped(db, statement):
    result = defaultdict(list)
    for row in db.execute(statement):
        values = dict(row)
        result[values.pop("case_id")].append(values)
    return result


def phi_coefficient(rows):
    table = {fmt: [0, 0] for fmt in FORMATS}
    for row in rows:
        table[row["format"]][0] += row["cited"]
        table[row["format"]][1] += row["probes"] - row["cited"]
    a, b = table["Fact table"]
    c, d = table["Prose"]
    denominator = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return (a * d - b * c) / denominator if denominator else None


def build_referrals():
    catalogue = json.loads((ROOT / "data/geo.json").read_text())["cases"]
    with sqlite3.connect(":memory:") as db:
        db.row_factory = sqlite3.Row
        db.executescript("""
            CREATE TABLE referrals(
                session_id TEXT PRIMARY KEY, case_id TEXT, channel TEXT, week INTEGER,
                carts INTEGER, purchases INTEGER
            );
            CREATE TABLE probes(
                case_id TEXT, week INTEGER, question_id TEXT, publisher TEXT,
                format TEXT, repeat INTEGER, cited INTEGER CHECK(cited IN (0, 1)),
                PRIMARY KEY(case_id, week, question_id, publisher, format, repeat)
            );
        """)
        for case_id, scenario in SCENARIOS.items():
            add_referrals(db, case_id, scenario)
            questions = [q["id"] for q in catalogue[case_id]["questions"]]
            add_probes(db, case_id, scenario, questions)
        channels = grouped(db, """
            SELECT case_id, channel, COUNT(*) AS n, SUM(carts) AS carts, SUM(purchases) AS purchases,
                   100.0 * AVG(carts) AS cart_rate_pct
            FROM referrals GROUP BY case_id, channel ORDER BY case_id, channel
        """)
        weekly = grouped(db, """
            SELECT case_id, week, COUNT(*) AS probes, SUM(cited) AS cited, 100.0 * AVG(cited) AS citation_rate_pct
            FROM probes GROUP BY case_id, week ORDER BY case_id, week
        """)
        sources = grouped(db, """
            SELECT case_id, publisher, format, COUNT(*) AS probes, SUM(cited) AS cited,
                   100.0 * AVG(cited) AS citation_rate_pct
            FROM probes GROUP BY case_id, publisher, format ORDER BY case_id, publisher, format
        """)
    cases = {}
    for case_id in SCENARIOS:
        by_channel = {r["channel"]: r for r in channels[case_id]}
        ai, organic, direct, unknown = [by_channel[k] for k in CHANNELS]
        total = sum(r["n"] for r in by_channel.values())
        cases[case_id] = {
            "sessions": total, "tagged_ai_sessions": ai["n"], "tagged_ai_share_pct": 100 * ai["n"] / total,
            "unknown_sessions": unknown["n"], "unknown_share_pct": 100 * unknown["n"] / total,
            "ambiguous_sessions": unknown["n"] + direct["n"],
            "tagged_ai_cart_rate_pct": ai["cart_rate_pct"], "organic_cart_rate_pct": organic["cart_rate_pct"],
            "observed_gap_pp": ai["cart_rate_pct"] - organic["cart_rate_pct"],
            "channels": [by_channel[k] for k in CHANNELS], "weekly": weekly[case_id], "sources": sources[case_id],
            "format_correlation_r": phi_coefficient(sources[case_id]),
        }
    return {
        "schema_version": "1.0", "source": "Synthetic referral labels plus a separate synthetic four-week citation panel.",
        "definitions": {"tagged_ai": "An explicit AI referral source tag in this scenario.",
                        "observed_gap_pp": "Tagged-AI cart rate minus organic-search cart rate; descriptive.",
                        "citation_rate_pct": "Probes citing their assigned publisher / all probes in a stratum, times 100.",
                        "format_correlation_r": "Phi correlation of fact-table format with citation, pooling all fixture probes."},
        "cases": stable_precision(cases),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=ROOT / "data/referrals.json", type=Path)
    args = parser.parse_args()
    payload = build_referrals()
    args.output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n")
    for case_id, case in payload["cases"].items():
        print(f"{case_id}: {case['tagged_ai_sessions']} tagged AI sessions, {case['observed_gap_pp']:+.2f} pp observed cart-rate gap")


if __name__ == "__main__":
    main()
