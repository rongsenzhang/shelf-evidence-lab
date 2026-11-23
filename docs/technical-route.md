# Technical route for v1.0

**Decision.** A retail content lead can fund one follow-up test. Select a SKU, verify that its revised copy answers a shopper need, check the quality of the behavioural evidence, then record the action and owner.

| Stage | Implementation | Acceptance check |
| --- | --- | --- |
| Scope | Read the official job pack, principal Flixmedia product and customer pages, named customer cases and comparable products. Form the null and minimum useful effect before inspecting trials. | Trace an intervention to a buyer question, an approved fact, a business outcome and an accountable stakeholder. |
| Ingest | Python generates one row per assigned session. SQLite aggregates by case, date, variant and device. The event and publishing interfaces are documented in the data contract. | Zero-event assignments count in the denominator. Arm totals reconcile to the original records. |
| Evaluate answers | Fixed shopping questions cross A/B content, with approved facts, source pointers and verbatim answer fixtures. A separate Logitech reading exercise records actual outputs from two isolated model contexts. | Inspect a supported claim, a stale or misleading citation and a justified abstention. |
| Measure discovery | A controlled synthetic four-week panel crosses SKU, query, source publisher, format and repeats. A separate channel layer counts observable AI-tagged and organic arrivals as well as direct and unknown traffic. | Recover numerators and denominators, report uncovered traffic and examine within-source comparisons. |
| Test retail outcomes | Estimate the intention-to-treat change in add-to-cart probability across all assigned sessions. Test the expected 50:50 allocation and inspect device standardisation and leave-one-day-out sensitivity. | Apply the fixed-horizon gate. A failed integrity check blocks an apparently attractive result. |
| Serve and transfer | GitHub Pages serves static HTML, CSS, JavaScript and four JSON resources over HTTPS. The browser supports deep links and can export the selected case as a decision brief. | Open the public site on a narrow viewport, inspect the evidence, record a note and export the brief. Reproduce the calculations without credentials. |

## From a public build to a company service

A partner pilot would inventory authorised feeds, map retailer identifiers and page revisions, then query validated aggregates from private BigQuery views. A server-side collector would capture repeated search answers by provider, locale, query, time and retrieved source URL. Version changes, missing answers and unsupported claims belong in the analytical record. A labelled query bank, blind dual review for disputed claims, a reserved holdout and a retailer-approved randomisation plan would precede deployment. The static public workbench uses the corresponding read-only JSON contract.

The unit for page discovery is a query response under specified conditions. For referral analysis it is an arriving session. For a rollout decision it is the randomised unit. Their identifiers and estimands differ. A join across all three requires agreed instrumentation, lawful access, deduplication and a design supporting the intended attribution. The current website makes no such individual-level join.

| Downloadable or readable input | What it supplies |
| --- | --- |
| [Experiment snapshot](../data/experiment.json) | Assignment, funnels, intervals, integrity checks and decisions |
| [GEO answer fixtures](../data/geo.json) | Source packets, modelled answers, approved facts and checked references |
| [Controlled observation](../data/observed.json) | Instructions, public source, captured answers, grades and limits |
| [Referral and citation snapshot](../data/referrals.json) | Tagged traffic coverage, channel comparisons and format/publisher citation panels |
