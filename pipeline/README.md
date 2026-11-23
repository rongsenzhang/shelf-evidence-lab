# Reproduce the retail experiment

From the repository root, Python 3.8+ with SQLite support is sufficient.

```sh
python3 pipeline/build.py
python3 -m unittest discover -s tests
python3 pipeline/build.py --export-csv /tmp/shelf-sessions.csv
```

The first command rebuilds `data/experiment.json`. The third also exports every assigned fictional session, including those with zero events. Use `--output /tmp/experiment.json` to write a separate snapshot. All seeds and fixture parameters are visible in `build.py`. Scenario parameters and seeds were chosen to exhibit three teaching cases. Their magnitudes do not estimate a vendor benefit.

## Data and unit of analysis

The input contract requires one row per unique assigned shopper session. All visits in the fixture are independent and occur once. Primary keys, allowed arms and count constraints are enforced in [the SQLite schema](../sql/schema.sql). Each product is paired with one retailer and locale. The variant records the assigned whole-page content version. Devices are Mobile and Desktop. The 28 daily cohorts run from 1 to 28 October 2026; every session has complete observation within that session.

| Column | Meaning |
|---|---|
| session_id | Unique identifier for an assignment, including sessions without events |
| day, device | ISO date of assignment and device class |
| case_id, retailer, locale | Product case, retailer and language-market |
| variant | Assigned control page or revised treatment page |
| engaged | At least one interaction with a product-content module in this session (0/1) |
| carts | At least one add-to-cart for the assigned SKU in this session (0/1) |
| purchases | At least one subsequent purchase of the SKU in the session (0/1) |

A shopper can add to cart without interacting with a content module. Engagement, add-to-cart and purchase rates use the full assigned-session denominator. Purchases are a subset of carts in this fixture. Outcome windows and cross-session purchases would need separate definitions using real retail data.

## Fixed-horizon decision protocol

The case-specific estimand is the intention-to-treat difference in the probability of any same-session add-to-cart. The treatment is the full revised page. The estimate from a valid trial applies to the enrolled audience and this channel. This design cannot attribute effects to individual page components, AI referrals or model citation. Count each assigned session once and analyse it in its assigned arm. No unexposed visitors are removed after assignment.

1. At the end of 28 days, compare observed counts with the planned 50:50 split. A Pearson chi-square test with one degree of freedom below p = 0.01 blocks inference and requires reconciliation of assignment, exposure and missing records. Passing the check alone cannot prove randomisation or validate event instrumentation.
2. Compute treatment minus control cart rate in percentage points, a two-sided 95% Newcombe hybrid confidence interval using Wilson score component intervals, and the relative change compared with control. Relative change is null if control has zero carts.
3. Increase pilot scope only when the lower 95% bound exceeds the illustrative +0.5 percentage-point minimum difference. If the interval does not clear this bar, plan a fresh powered confirmatory trial. This fixed-horizon review allows no repeated looks or optional stopping. The +0.5 pp floor is an independent demonstrator policy and would require commercial agreement.
4. Inspect effect estimates by device, standardise them to the pooled device distribution and drop each day in turn. Those analyses diagnose sensitivity and do not supply additional decision gates. Engagement and purchase counts describe secondary outcomes. The prototype makes separate case-specific decisions with no portfolio-wide significance claim. A live multi-SKU programme would agree a multiplicity policy before ranking confirmed wins.

The deliberately imbalanced speaker case retains the arithmetic result so reviewers can diagnose why an attractive estimate fails the validity gate. Real deployment also needs a record of exclusions and missing events, durable shopper allocation or cluster-aware inference if people return, consistent retailer identifiers, production QA and cost/margin data for commercial sign-off.

## Warehouse adapter and public HTTP contract

`sql/daily_arms.sql` supplies the actual SQLite aggregation used by the build and uses syntax compatible with BigQuery GoogleSQL. To evaluate in BigQuery, upload the exported CSV into a test dataset as a table named `trial_sessions`, skip its header, use STRING for the identifiers, DATE for `day` and INT64 for the three event columns. In the supplied query replace the table identifier with a fully qualified backtick-quoted identifier such as `project.dataset.trial_sessions`, or configure a default dataset. Run the SELECT and reconcile arm totals to the public JSON. The reference implementation has been executed locally with SQLite. Cloud execution requires a provisioned project.

For a partner deployment, map authorised supplier exports to this contract, attach retailer consent scope, validate exposure and identity, and join events to the full assignment table before aggregation. Flixmedia publicly documents data access via Analytics Hub and BigQuery. The prototype uses its own schema and has no connection to a partner dataset. [Flixmedia Smart Insights](https://www.flixmedia.com/measure-optimise-content)

The public app can GET `data/experiment.json` relative to its hosted base URL. The versioned JSON object contains a source label, protocol and a `cases` map keyed by product ID. Each case includes arm counts, pooled effects, sample-ratio p-value, decision, rationale, device summaries, daily counts and sensitivity results. Rate denominators are in each arm's `n`. Outputs from model-answer evaluations live in a separate dataset.

## Methods

Newcombe's method 10 combines Wilson intervals for two independent proportions. The published procedure avoids the poor boundary behaviour of ordinary Wald difference intervals. See the original analysis for coverage comparisons. [Newcombe (1998), Statistics in Medicine](https://pubmed.ncbi.nlm.nih.gov/9595617/)

Sample-ratio mismatch flags potential problems with assignment or observation. Its practical use and potential root causes are described by Fabijan and colleagues. [Fabijan et al. (2019), KDD](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/)
