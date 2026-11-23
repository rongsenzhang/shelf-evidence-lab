"""Build a closed-book, synthetic UK product-page answer audit. Standard library only.

Run ``python3 pipeline/geo.py`` from the repository root to write data/geo.json.
The public contract is {schema_version, provenance, method, cases}. Each case has
name, market, retailer, business_question, revision, versions, questions, records,
metrics and interpretation. Versions A/B are current/revised PDPs. Records join to
questions via question_id and to the active version's passages via citation_id.
Metrics count all records including abstentions. A citation is valid if the quoted
text occurs in the named passage of the version shown. Support additionally needs
an exact approved answer and a citation containing a manually mapped evidence span.
The codebook scores these authored fixtures only; it is not an open-text evaluator.
"""
import json
from pathlib import Path


OUTPUT = Path(__file__).resolve().parents[1] / "data" / "geo.json"
ABSTAIN = "The supplied page does not establish this."

# A passage is a list of sentences. Question-specific evidence is bound to an
# exact (passage, sentence) position in each content version, when available.
CASES = {
    "headphones": {
        "name": "Arc One headphones", "retailer": "Northline Electrical",
        "business_question": "Will clearer battery and charging guidance help commuters choose the Arc One and add it to their basket?",
        "revision": "Replace vague battery and charging copy with ANC-on and ANC-off limits, a timed top-up and a clear statement about USB-C audio.",
        "A": [["Wireless over-ear headphones with active noise cancellation (ANC).", "Enjoy up to 40 hours between charges."],
              ["Top up quickly over USB-C.", "An analogue cable is supplied for wired listening."]],
        "B": [["With ANC on, rated battery life is up to 24 hours.", "With ANC off, rated battery life is up to 40 hours."],
              ["A 10-minute top-up provides up to 3 hours of playback.", "USB-C is for charging only; use the supplied analogue cable for wired audio."]],
        "questions": [
            ("anc-on", "How long can I listen with noise cancellation switched on?", "Up to 24 hours with ANC on.", "Up to 40 hours with ANC on.", None, (0, 0)),
            ("anc-off", "What is the maximum rated playback time with ANC off?", "Up to 40 hours with ANC off.", "Up to 24 hours with ANC off.", None, (0, 1)),
            ("top-up", "How much playback does a 10-minute charge provide?", "Up to 3 hours of playback.", "Up to 10 hours of playback.", None, (1, 0)),
            ("usb-audio", "Can I listen to audio through the USB-C socket?", "No. USB-C is for charging only.", "Yes. USB-C carries digital audio.", None, (1, 1)),
        ],
        # Per question, two A and two B examples. 'other' quotes genuine but insufficient copy.
        "responses": [
            (("wrong:other", "skip"), ("right:proof", "right:proof")),
            (("right:other", "right"), ("right:proof", "right:proof")),
            (("skip", "wrong"), ("right:proof", "right:proof")),
            (("wrong:other", "skip"), ("right:proof", "right")),
        ],
        "interpretation": "The revised copy gives a reviewer evidence for each battery and charging answer. One correct example still lacks a citation. Use fresh engine observations to test whether assistants actually find and cite this page.",
    },
    "monitor": {
        "name": "Forma 27 monitor", "retailer": "Field & Frame",
        "business_question": "Does specifying USB-C power delivery and cable requirements reduce compatibility uncertainty enough to increase basket additions?",
        "revision": "State the maximum USB-C power delivery, video protocol and included lead alongside the existing 27-inch screen size.",
        "A": [["The screen measures 27 inches diagonally.", "A single USB-C connection keeps your desk tidy."],
              ["A USB-C lead is supplied.", "Connect a compatible laptop for a simple desk setup."]],
        "B": [["The screen measures 27 inches diagonally.", "The upstream USB-C port delivers up to 65 W to a compatible laptop."],
              ["USB-C video requires DisplayPort Alt Mode on the laptop.", "A full-featured USB-C to USB-C cable supporting video and 65 W charging is supplied."]],
        "questions": [
            ("power", "What is the highest charging power the monitor can supply to my laptop?", "Up to 65 W.", "Up to 100 W.", None, (0, 1)),
            ("video", "What must my laptop USB-C port support to show video on this monitor?", "DisplayPort Alt Mode.", "Any charge-only USB-C port will work.", None, (1, 0)),
            ("cable", "Does the included USB-C cable support both video and 65 W charging?", "Yes. The supplied cable supports video and 65 W charging.", "No. The supplied cable is charge-only.", None, (1, 1)),
            ("size", "How large is the screen, measured diagonally?", "27 inches.", "32 inches.", (0, 0), (0, 0)),
        ],
        "responses": [
            (("skip", "wrong:other"), ("right:proof", "right:proof")),
            (("wrong:other", "skip"), ("right:proof", "skip")),
            (("right:other", "right"), ("right:proof", "right:stale")),
            (("right:proof", "right:proof"), ("right:proof", "right:proof")),
        ],
        "interpretation": "The revised port specification makes compatibility claims checkable. One example abstains and another points to a stale passage ID. The unchanged screen-size question provides a stable comparison.",
    },
    "speaker": {
        "name": "Tide Mini speaker", "retailer": "Northline Electrical",
        "business_question": "Does qualified wording about water resistance and battery life help shoppers choose the Tide Mini without overstating what it can do?",
        "revision": "Give the water-resistance rating and use limits, qualify the battery claim by volume, and keep the charging connector explicit.",
        "A": [["Take your water-resistant speaker outdoors.", "The rated battery life is up to 12 hours."],
              ["Recharge the speaker over USB-C.", "A compact design fits neatly in a day bag."]],
        "B": [["The enclosure has an IPX5 water-resistance rating.", "It can handle water jets but must not be submerged."],
              ["Rated battery life is up to 12 hours at 50% volume.", "Recharge the speaker over USB-C."]],
        "questions": [
            ("rating", "What is the speaker's water-resistance rating?", "IPX5.", "IP67.", None, (0, 0)),
            ("submersion", "Can this speaker be submerged in water?", "No. It must not be submerged.", "Yes. It can be submerged.", None, (0, 1)),
            ("battery", "At what volume is the 12-hour battery figure rated?", "At 50% volume.", "At full volume.", None, (1, 0)),
            ("port", "Which connector recharges the speaker?", "USB-C.", "Micro-USB.", (1, 0), (1, 1)),
        ],
        "responses": [
            (("skip", "wrong:other"), ("right:proof", "right:proof")),
            (("wrong:other", "skip"), ("right:proof", "wrong:proof")),
            (("right", "wrong"), ("right:proof", "right:other")),
            (("right:proof", "right:proof"), ("right:proof", "right:proof")),
        ],
        "interpretation": "A revised-page example cites the actual warning but reverses its meaning. Citation presence alone would miss this error. Before publication, a content owner should check this question across independent live answers.",
    },
}


def passage_id(case_id, version, index):
    return f"{case_id}-{version}-{index + 1}"


def make_record(case_id, spec, question, version, repeat, scenario):
    fact_id, _, truth, wrong, a_evidence, b_evidence = question
    evidence = a_evidence if version == "A" else b_evidence
    choice, _, reference = scenario.partition(":")
    answer = {"right": truth, "wrong": wrong, "skip": ABSTAIN}[choice]
    cite_id = quote = None
    if reference:
        if reference == "other":
            # Prefer a sentence from the same topic. For an annotated question,
            # use the other sentence in its passage, so evidence is insufficient.
            pointer = (evidence[0], 1 - evidence[1]) if evidence else {
                "anc-on": (0, 1), "anc-off": (0, 1), "usb-audio": (1, 0),
                "power": (0, 1), "video": (1, 1), "cable": (1, 0),
                "rating": (0, 0), "submersion": (0, 0),
            }[fact_id]
        elif reference in {"proof", "stale"} and evidence is not None:
            pointer = evidence
        else:
            raise ValueError(f"Unrecognised or unavailable reference {scenario} for {fact_id}")
        cite_id = passage_id(case_id, version, pointer[0])
        quote = spec[version][pointer[0]][pointer[1]]
        if reference == "stale":
            cite_id = passage_id(case_id, "A" if version == "B" else "B", pointer[0])
    return {"question_id": fact_id, "version": version, "repeat": repeat,
            "answer": answer, "citation_id": cite_id, "citation_quote": quote}


def evaluate(record, truth, passages, evidence):
    """Score a canonical fixture response and verify its citation against this version."""
    answer = record["answer"]
    verdict = "abstain" if answer == ABSTAIN else ("correct" if answer == truth else "incorrect")
    quote = record["citation_quote"]
    cited_passage = passages.get(record["citation_id"], "")
    valid = bool(quote and quote in cited_passage)
    supported = bool(valid and verdict == "correct" and evidence
                     and record["citation_id"] == evidence["passage_id"]
                     and evidence["quote"] in quote)
    return {**record, "verdict": verdict, "citation_valid": valid, "supported": supported}


def metrics(records):
    total = len(records)
    counts = {v: sum(row["verdict"] == v for row in records) for v in ("correct", "incorrect", "abstain")}
    cited = sum(row["citation_id"] is not None for row in records)
    valid = sum(row["citation_valid"] for row in records)
    supported = sum(row["supported"] for row in records)
    return {"total": total, **counts, "cited": cited, "valid_citations": valid, "supported": supported,
            "accuracy": counts["correct"] / total, "citation_rate": cited / total,
            "valid_citation_rate": valid / total, "support_rate": supported / total}


def build_case(case_id, spec):
    case = {key: spec[key] for key in ("name", "retailer", "business_question", "revision", "interpretation")}
    case.update(market="UK · en-GB", versions={}, questions=[], records=[], metrics={})
    for version, label in (("A", "Current page"), ("B", "Revised page")):
        passages = {passage_id(case_id, version, i): " ".join(text) for i, text in enumerate(spec[version])}
        case["versions"][version] = {"label": label, "passages": [{"id": k, "text": v} for k, v in passages.items()]}
        for number, question in enumerate(spec["questions"]):
            fact_id, prompt, truth, _, a_span, b_span = question
            if version == "A":
                case["questions"].append({"id": fact_id, "text": prompt, "truth": truth, "fact_id": f"{case_id}/{fact_id}", "evidence": {}})
            span = a_span if version == "A" else b_span
            evidence = None if span is None else {"passage_id": passage_id(case_id, version, span[0]), "quote": spec[version][span[0]][span[1]]}
            case["questions"][number]["evidence"][version] = evidence
            examples = spec["responses"][number][0 if version == "A" else 1]
            for repeat, example in enumerate(examples, start=1):
                row = make_record(case_id, spec, question, version, repeat, example)
                case["records"].append(evaluate(row, truth, passages, evidence))
        case["metrics"][version] = metrics([r for r in case["records"] if r["version"] == version])
    return case


def build():
    return {
        "schema_version": "1.0", "provenance": "Authored synthetic product facts, UK page excerpts and answer fixtures. No live engine calls or retailer data.",
        "method": {
            "panel": "Four fixed shopper questions per product, two authored response fixtures per version and question. Each A/B pair uses the same prompt. Repeat numbers identify illustrative traces, not independent engine runs.",
            "accuracy": "Exact match to the approved synthetic answer divided by all responses, including abstentions. This finite codebook applies only to the supplied fixtures.",
            "citation_rate": "Responses naming a passage divided by all responses, including stale references.",
            "valid_citation_rate": "Responses quoting the named passage in the presented version divided by all responses. A valid quote may be irrelevant or contradict the answer.",
            "support_rate": "Correct answers with a valid citation containing the question's annotated evidence span divided by all responses.",
            "limits": "This is a closed-book answer-grounding audit. Public engine inclusion, rank, citation frequency, stochastic variation and effects on shopping behaviour require independently collected evidence. Fixture differences are illustrative only.",
        },
        "cases": {case_id: build_case(case_id, case) for case_id, case in CASES.items()},
    }


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
