"""Recreate the public experiment evidence with Python's standard library."""
import argparse
import csv
from datetime import date, timedelta
import json
import math
from pathlib import Path
import random
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
START = date(2026, 10, 1)
DAYS = 28
Z95 = 1.959963984540054
MIN_EFFECT_PP = 0.5
SRM_ALPHA = 0.01
ARM_NAMES = ("control", "treatment")
COUNTS = ("n", "engaged", "carts", "purchases")
COLUMNS = ("session_id", "day", "case_id", "retailer", "locale", "device",
           "variant", "engaged", "carts", "purchases")

# Unobservable fixture parameters. The estimator only receives observed session rows.
# The speaker trial deliberately violates its preregistered 50:50 allocation.
SCENARIOS = {
    "headphones": {"retailer": "Northline Electrical", "seed": 317, "daily_n": 520,
                   "cart_rate": 0.080, "cart_delta": 0.029, "allocation": 0.50},
    "monitor": {"retailer": "Field & Frame", "seed": 102, "daily_n": 115,
                "cart_rate": 0.068, "cart_delta": 0.004, "allocation": 0.50},
    "speaker": {"retailer": "Northline Electrical", "seed": 401, "daily_n": 270,
                "cart_rate": 0.087, "cart_delta": 0.024, "allocation": 0.61},
}


def make_rows(case_id, scenario):
    rng = random.Random(scenario["seed"])
    for day_no in range(DAYS):
        day = START + timedelta(days=day_no)
        weekend = day.weekday() >= 5
        sample = round(scenario["daily_n"] * (1.11 if weekend else 1.0))
        for visitor in range(sample):
            mobile = rng.random() < (0.68 if weekend else 0.57)
            treatment = rng.random() < scenario["allocation"]
            rate = (scenario["cart_rate"] + 0.018 * (not mobile) + 0.005 * weekend
                    + scenario["cart_delta"] * treatment)
            engaged = rng.random() < 0.34 + 0.06 * (not mobile) + 0.04 * treatment
            cart = rng.random() < rate
            purchase_draw = rng.random()
            yield (f"{case_id}-{day_no:02}-{visitor:04}", day.isoformat(),
                   case_id, scenario["retailer"], "en-GB", "Mobile" if mobile else "Desktop",
                   "treatment" if treatment else "control", int(engaged), int(cart),
                   int(cart and purchase_draw < 0.36))


def empty_arms():
    return {arm: dict.fromkeys(COUNTS, 0) for arm in ARM_NAMES}


def add_counts(total, row):
    for key in COUNTS:
        total[key] += row[key]


def wilson(successes, n):
    """Wilson score interval for a single binary rate."""
    p = successes / n
    denominator = 1 + Z95**2 / n
    centre = (p + Z95**2 / (2 * n)) / denominator
    radius = Z95 * math.sqrt(p * (1 - p) / n + Z95**2 / (4 * n**2)) / denominator
    return max(0, centre - radius), min(1, centre + radius)


def difference(arms, metric="carts"):
    """Newcombe hybrid score interval for independent treatment minus control risks."""
    control, treatment = (arms[arm] for arm in ARM_NAMES)
    pc = control[metric] / control["n"]
    pt = treatment[metric] / treatment["n"]
    cl, cu = wilson(control[metric], control["n"])
    tl, tu = wilson(treatment[metric], treatment["n"])
    delta = pt - pc
    lower = delta - math.hypot(pt - tl, cu - pc)
    upper = delta + math.hypot(tu - pt, pc - cl)
    return {"effect_pp": 100 * delta, "ci_low_pp": 100 * lower,
            "ci_high_pp": 100 * upper, "relative_lift_pct": 100 * delta / pc if pc else None}


def srm_p(n_control, n_treatment):
    """Pearson chi-square p-value with one df, for planned 50:50 exposure."""
    z = abs(n_control - n_treatment) / math.sqrt(n_control + n_treatment)
    return math.erfc(z / math.sqrt(2))


def decide(balance_p, lower):
    if balance_p < SRM_ALPHA:
        return ("Hold for investigation",
                "Allocation breaches the 50:50 balance check. Reconcile assignment and exposure logs, repair the split and rerun before interpreting the effect.")
    if lower > MIN_EFFECT_PP:
        return ("Advance to pilot",
                "The lower 95% bound exceeds the prespecified +0.5 percentage-point threshold. Review the change with the retailer and test transfer to a second channel.")
    return ("Collect more evidence",
            "The fixed-horizon interval does not clear +0.5 percentage points. Design a new adequately powered test before expanding distribution.")


def summarise(case_id, rows):
    totals = empty_arms()
    dates = {}
    devices = {}
    for row in rows:
        arm = row["variant"]
        add_counts(totals[arm], row)
        add_counts(dates.setdefault(row["day"], empty_arms())[arm], row)
        add_counts(devices.setdefault(row["device"], empty_arms())[arm], row)

    effects = difference(totals)
    balance = srm_p(totals["control"]["n"], totals["treatment"]["n"])
    decision, reason = decide(balance, effects["ci_low_pp"])
    strata = [{"device": device, **arms, **difference(arms)} for device, arms in sorted(devices.items())]
    sample_size = sum(arm["n"] for arm in totals.values())
    adjusted = sum(stratum["effect_pp"] * (stratum["control"]["n"] + stratum["treatment"]["n"])
                   / sample_size for stratum in strata)
    leave_one_out = []
    for daily in dates.values():
        rest = {arm: {key: totals[arm][key] - daily[arm][key] for key in COUNTS} for arm in ARM_NAMES}
        leave_one_out.append(difference(rest)["effect_pp"])

    return {
        "id": case_id, "retailer": rows[0]["retailer"], "locale": rows[0]["locale"],
        "start_date": min(dates), "end_date": max(dates), **totals, **effects,
        "balance_p": balance, "decision": decision, "reason": reason, "devices": strata,
        "sensitivity": {"standardised_effect_pp": adjusted, "leave_one_day_out_min_pp": min(leave_one_out),
                        "leave_one_day_out_max_pp": max(leave_one_out)},
        "daily": [{"date": day, **daily} for day, daily in sorted(dates.items())],
    }


def stable_precision(value):
    """Keep published floats reproducible across platform math libraries."""
    if isinstance(value, float):
        return float(format(value, ".10g"))
    if isinstance(value, dict):
        return {key: stable_precision(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stable_precision(item) for item in value]
    return value


def build(export_csv=None):
    with sqlite3.connect(":memory:") as db:
        db.row_factory = sqlite3.Row
        db.executescript((ROOT / "sql/schema.sql").read_text())
        for case_id, scenario in SCENARIOS.items():
            db.executemany("INSERT INTO trial_sessions VALUES (?,?,?,?,?,?,?,?,?,?)", make_rows(case_id, scenario))
        if export_csv:
            with Path(export_csv).open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(COLUMNS)
                writer.writerows(db.execute("SELECT * FROM trial_sessions ORDER BY session_id"))
        rows = db.execute((ROOT / "sql/daily_arms.sql").read_text()).fetchall()

    cases = {key: summarise(key, [row for row in rows if row["case_id"] == key]) for key in SCENARIOS}
    return {
        "schema_version": "1.0", "source": "Seeded synthetic UK retail trial; fictional products and retailers",
        "protocol": {"unit": "one unique, independent shopper session", "horizon_days": DAYS,
                     "planned_treatment_share": 0.5, "balance_test": "Pearson chi-square, one df",
                     "srm_alpha": SRM_ALPHA, "primary": "assigned sessions with at least one add-to-cart / assigned sessions",
                     "effect": "treatment minus control, percentage points",
                     "ci": "two-sided 95% Newcombe hybrid interval with Wilson component intervals",
                     "minimum_effect_pp": MIN_EFFECT_PP, "secondary": ["engagement", "purchase"],
                     "scope": "Case-by-case hypotheses. Device and leave-one-day-out results are descriptive sensitivity checks."},
        "cases": stable_precision(cases),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-csv", type=Path, help="also export all synthetic assigned sessions")
    parser.add_argument("--output", type=Path, default=ROOT / "data/experiment.json")
    args = parser.parse_args()
    payload = build(args.export_csv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n",
                           encoding="utf-8")
    for key, trial in payload["cases"].items():
        print(f"{key}: {trial['effect_pp']:+.2f} pp [{trial['ci_low_pp']:+.2f}, {trial['ci_high_pp']:+.2f}] — {trial['decision']}")


if __name__ == "__main__":
    main()
