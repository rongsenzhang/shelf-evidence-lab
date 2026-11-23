# Referral outcomes and citation-source trends

A retailer has two practical questions. Which tagged visitors add the product to cart, and which kinds of source appear in shopping answers? This demonstrator has two different units: one assigned shopper session for the first question, one answer probe for the second. A citation can appear without a click, and a referral can arrive without an observable answer. The two datasets have no person-level linkage.

## Referral attribution

The analysis adds a deterministic acquisition label to each of the 26,140 synthetic trial sessions. All sessions and their existing cart and purchase outcomes reconcile to the trial. The channel generator uses device and week before inspecting outcomes. Tags are observational, unlike the page version assignment. Week, device and visitor intent can produce different cart rates even when acquisition itself has no effect.

| Channel | Meaning in this fixture |
|---|---|
| Tagged AI | An unambiguous AI source tag recorded for the visit |
| Organic search | A recognised organic search source |
| Direct / untagged | A visit without a recognised referral tag, including typed or untagged arrivals |
| Unknown / missing | A damaged, missing or unmapped source record in the fixture |

Compute tagged AI share as tagged AI sessions divided by all sessions. The observed commercial difference is cart rate for tagged AI visits minus cart rate for organic search visits, expressed in percentage points. Counts of purchases, carts and total sessions are available for all four channels. Do not estimate AI-attributable revenue or incrementality from this difference. Acquiring an unexposed comparison group or a suitably designed incrementality study is a different task.

For Arc One, 1,577 of 15,016 visits have explicit AI tags (10.50%). The tagged-cart-rate gap against organic is +1.67 percentage points, and 15.46% of all visits have missing or unmapped source records. Direct/untagged traffic is another ambiguous category. Investigate tag retention through redirects and app-to-browser transitions before claiming a change in channel mix. The labels are the project's data contract. Google separately explains that its direct classification can include traffic without a clear referrer. [Google Analytics Help](https://support.google.com/analytics/answer/15258820?hl=en)

## Citation panel

Each of the four catalogue questions per SKU is observed at four weekly checkpoints against six publisher/format combinations, with four repeats per cell. Publishers are Brand, Retailer and Editorial. Each supplies both a fact table and prose in the artificial design. That yields 96 trials per SKU per week and 1,152 probes across all cases. The observation is a simulated binary indicator of whether the assigned source is cited. Neither marketplace pages nor model outputs were fetched for this panel. The separate answer audit in the workbench records page passages and answer support.

The SQLite query computes weekly citation counts/rates and the six source-by-format rates. The phi coefficient is the Pearson correlation of two binary indicators, fact-table format and citation present. Positive values mean fact-table probes were cited more often in this fixture. A complete balanced design reduces differences from unequal question counts across publisher and format groups. Correlation is descriptive. The generator includes different citation propensities across publisher, format and period, so an observed association is a demonstration of how to audit signals, not a discovery about shopping engines. No standard errors treating the repeated prompts as independent are reported.

For Arc One, the weekly rates are 43.75%, 42.71%, 42.71% and 51.04%; the pooled format-citation correlation is +0.120. A programme owner could use the method to nominate one page format for an independently pre-registered field evaluation. Live work would freeze prompt wording and locale, record engine, model revision, surface, timestamp, URL and citation position, version the source passages, blind human adjudicators to treatment, and keep an explicit record of missing runs.

## Rebuild

From the repository root:

```sh
python3 pipeline/geo.py
python3 pipeline/referrals.py
python3 -m unittest discover -s tests
```

The endpoint is `data/referrals.json`. The pipeline reads the catalogue question IDs, recreates the seeded trial sessions, generates the two independent fixtures and aggregates both with SQL. Inspect [the source](../pipeline/referrals.py) for the simulation parameters and exact aggregation.
