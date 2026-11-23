# Can a clearer product claim help a shopper decide?

A brand can improve the wording on its product page, see more AI answers cite it, and still gain no additional orders. This protocol identifies the evidence each decision requires. The fictional retail cases exercise the method. The separate reading of published Logitech material is a bounded observation of public content. Neither yields a commercial effect estimate for Logitech or Flixmedia.

## What runs in v1.0

The generator creates one independent session per assignment. SQLite aggregates all assigned sessions, including those with zero engagement. The Python analysis estimates an add-to-cart risk difference with a two-sided 95% Newcombe interval using Wilson component intervals. It tests the planned 50:50 split using Pearson's chi-squared test with one degree of freedom. Secondary engagement and purchase outcomes and device or leave-one-day-out sensitivity results are descriptive. [Generator and estimator](../pipeline/build.py) · [Aggregation SQL](../sql/daily_arms.sql) · [Computed evidence](../data/experiment.json)

The headphone case advances to a second pilot in the simulation. Its two rates are 726/7,460 and 876/7,556, a difference of +1.86 percentage points (95% interval +0.87 to +2.85). The monitor case has insufficient evidence and the speaker case fails the allocation check. Selecting these three scenarios deliberately illustrates three decisions. The distribution of outcomes does not estimate how frequently real edits succeed. [Computed evidence](../data/experiment.json)

## Questions and units for a partner pilot

| Question | Comparison and population | Outcome |
| --- | --- | --- |
| Does the proposed copy help an answer engine give a verifiable answer? | Compare versions of the same product fact under the same prompt, locale, engine, source set and retrieval conditions. Repeat runs and record the date and model identifier available from the provider. | Within each condition, count answers that identify the correct product, cite an eligible source and accurately support the specific claim. Report component numerators and denominators. |
| Does offering the revision change shopping behaviour? | Assign eligible shoppers 50:50 to the existing retailer page or the revised page, keeping allocation sticky over the 28-day test. | Primary outcome is whether an assigned shopper adds the tested SKU to their basket. Estimate the difference in rates between arms in percentage points. |

The first question concerns source use and factual accuracy. Aggarwal and colleagues define generative-engine visibility at the level of an answer and find that interventions vary in effectiveness across domains. A subsequent review emphasises the distinction between finding a source and citing one already supplied to the model. It motivates the matched-prompt design and separate reporting of retrieval conditions. [Aggarwal et al., KDD 2024](https://arxiv.org/abs/2311.09735) · [Martinez, 2026 preprint](https://arxiv.org/abs/2607.14035)

For real traffic, prefer shopper-level assignment when an approved identifier is available. Repeated visits by the same person then contribute a single outcome within the observation window. This differs from v1.0's independent-session assumption and requires a new denominator and power calculation.

### Answer evaluation

1. Before collecting answers, register the shopper intent, acceptable source URLs, verbatim specification and any qualifying condition. For a claim about compatibility, record which model and connection method the specification covers.
2. Include direct questions, paraphrases, unbranded shopping questions and a question the source cannot answer. Keep a fixed panel for comparison and reserve additional prompts for checking generalisation.
3. Retain the response, source URL, engine identifier, run time and any access failure. A reviewer records whether the quoted passage supports the answer. Cite coverage uses all completed responses as the denominator. Separately report attempted runs, unavailable answers and missing citations, so a broken run cannot improve the score.
4. For repeated observations, pair at the prompt level, randomise source order where possible and report uncertainty across prompts. Cross-engine and cross-day panels test whether the finding travels. A fixed-source model reading measures use of supplied material. Measuring organic discovery requires a separate arm in which the engine finds its own sources.

## Retail pilot protocol

| Decision | Specification to register before the pilot |
| --- | --- |
| Treatment | One versioned change to an approved claim and its placement. Preserve screenshots of both page variants, including the mobile layout. Keep price, offers and fulfilment conditions comparable. Log interruptions and stock-outs. |
| Eligibility | Visitors to the selected in-stock SKU and retailer during the 28-day window. Define bot filtering, consent conditions and the counting window before assignment. Use the same observation window for both arms and allow late outcomes to mature. |
| Assignment and exposure | Randomise at first eligibility, retain the same variant across repeat visits and deduplicate by the permitted shopper identifier. Report assigned and exposed counts. Analyse all eligible assignments, including people who never scrolled to the revision. |
| Estimand | Intention-to-treat difference in the probability of at least one add-to-cart for the tested SKU. Subtract control rate from treatment rate, using unique assigned shoppers per arm. A rise from 5% to 6% is +1 percentage point and +20% relative. |
| Adequacy | Before launch, estimate sample needs from historical baseline, minimum worthwhile effect and chosen power. Check the 28-day traffic forecast against the requirement. A small retailer may need more SKUs or a separately planned trial. |
| Analysis | Close at the fixed 28-day horizon. Calculate the absolute difference and its 95% interval. Check the observed allocation against 50:50. A sample-ratio-mismatch p-value below 0.01 triggers an investigation of assignment and event loss. |
| Action | Advance the revision for rollout review only if the allocation check passes and the lower 95% bound exceeds +0.5 percentage points. Otherwise retain the control pending more evidence or repair the instrumentation. The 0.5-point hurdle is a portfolio assumption. Agree the actual margin and cost threshold with the retailer before a pilot. |

Randomisation supports a causal interpretation when assignment persists, outcomes are captured comparably and one shopper's assignment does not alter another shopper's exposure. A shared syndicated asset can leak across retailer pages. Serve immutable variant versions and inspect control pages before launch. If assignment must occur by retailer or URL, use cluster-aware design and uncertainty estimates. The number of independent units then becomes a constraint. [Kohavi et al., 2009](https://exp-platform.com/journal-survey/) · [Fabijan et al., KDD 2019](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/)

### Robustness and interpretation

- Report results by device and retailer next to the pooled estimate. Check differences in stock, price, content loading and tracking coverage. Treat unplanned subgroup comparisons as exploratory.
- Track qualified purchases, revenue per assigned shopper and page-load performance if partners can supply them. A positive add-to-cart effect alone supports a basket claim. Sales and profit require downstream observations, unit economics and fulfilment costs.
- Prioritising many edits can select lucky winners. Confirm a candidate in fresh traffic or reserve a holdout before wider rollout. Any predictive score used for triage should be checked on held-out data against a simple baseline. Its ranking orders work for review.
- The synthetic cases can demonstrate calculation, poor precision and a failed quality gate. Their numerical results depend on the generator. The selected product, prompt and date in the public observation limit inference about other products, model behaviour, live search, actual buyers and demand.

The academic output proposed for a partner pilot is a short methods paper with a registered intervention, explicit estimand, missing-data report and reproducible tables. Company and university reviewers would agree disclosure and publication terms before partner data were used.

## A public web-retrieval check

On 23 November 2026 two independent web-enabled Codex readers each answered one UK shopping question. Each was allowed one search query and up to three page opens. These are additional observed answers alongside the source-only keyboard exercise. The model chose and executed the query in each case. Formatting and citation tokens have been removed from the quotations of the generated answers.

| Observation | Shopper's prompt | Search query actually executed | Answer recorded and URL cited |
| --- | --- | --- | --- |
| Branded | For a UK office buying a Logitech MX Keys Mini for Business, is a receiver in the box, and how many computers can one keyboard switch between? | `site:logitech.com/en-gb MX Keys Mini for Business Logi Bolt USB receiver in the box Easy-Switch three computers` | “Yes. The UK Logitech MX Keys Mini for Business includes a Logi Bolt USB-A receiver. Its Easy-Switch keys let one keyboard switch between up to three paired computers.” [Captured source](https://www.logitech.com/en-gb/products/keyboards/mx-keys-mini-for-business.html?bvstate=pg%3A2%2Fct%3Ar) |
| Need-led | Which compact wireless office keyboard sold in the UK includes a USB receiver and lets me switch among three computers? Name one model and identify the source for both claims. | `Logitech MX Keys Mini for Business UK included Logi Bolt USB receiver Easy-Switch three computers compact keyboard UK buy Logitech` | “Logitech MX Keys Mini for Business. Logitech’s UK product page lists a Logi Bolt USB-A receiver under ‘In the Box’ and confirms under ‘Connect Multiple Devices’ that the Easy-Switch keys switch among up to three paired computers.” [Captured source](https://www.logitech.com/en-gb/products/keyboards/mx-keys-mini-for-business.html?bvstate=pg:2/ct:r) |

Both responses cited the manufacturer's business-edition page. The internal query for the need-led question already contains the brand and model. Treating it as an unbranded search win would overstate the evidence. This run illustrates why analysts should preserve the shopper prompt **and** the retrieval query when observable. A larger pilot would preregister neutral retrieval constraints, vary the engines and repeat prompts. These two observations cannot establish competitive visibility share or a causal benefit from editing a page. [UK part-specific product reference](https://www.logitech.com/en-gb/products/keyboards/mx-keys-mini-for-business.920-010611.html)
