# Data Product Analyst KTP · CC14066

The University of Bath School of Management and Flixmedia seek a quantitative marketing researcher and project lead to build a decision platform for generative engine optimisation (GEO). The deliverable is a capability the business can operate: decide which retail content change to make, test it, challenge the evidence and communicate the result. This independent work sample illustrates the methods using public evidence and fictional retail trials. [Vacancy](https://www.bath.ac.uk/jobs/Vacancy.aspx?ref=CC14066) · [Official job description and person specification, Word](https://www.bath.ac.uk/jobs/Upload/vacancies/files/30288/Flixmedia%20JD.doc)

## Conditions and candidate profile

The advert gives a starting salary of £50,000, an 18-month full-time contract, a closing date of 25 November 2026 and an interview date of 10 December 2026. The university employs the Associate, who works primarily at the company's London office. The advert mentions scope for hybrid working. The attachment describes the position as on-site and allows up to 15% travel to Bath. The package includes a £3,000 development budget, 10% development time and two residential modules. The university assesses UK work eligibility at offer stage. The job pack requires the right to work at appointment.

The qualification route is a quantitatively oriented marketing PhD or a related discipline, or a relevant master's degree with three or more years of qualifying experience in quantitative marketing research, analytics or data-driven product innovation. The experience specification covers data analysis, API systems, cloud platforms, UX, data visualisation, content workflows, commercial recommendations, project management and quantitative methods. The public advert calls for R or Python, SQL with BigQuery preferred, and familiarity with GEO. Experimentation, causal inference, econometrics and ML are examples of relevant methods.

Candidates are asked for evidence of research design, interpretation, reproducibility, research communication, academic outputs, stakeholder management and completion of multidisciplinary work. Supply personal examples with dates, contribution and outcomes. Degree eligibility, individual authorship, publications, stakeholder relationships and work permissions must be substantiated separately in the application.

## The 17 official responsibilities

Numbers track the order in the job attachment. Each row identifies what a reviewer can inspect and the work a partner project would still require.

| Duty | Evidence in v1.0 | At a partner deployment |
| --- | --- | --- |
| 1. Identify formats and structures for LLM discovery and citation | [Format and publisher comparison](referrals.md), [controlled answers](../data/observed.json) and [two web-retrieval observations](research-design.md#a-public-web-retrieval-check). | Run content ablations with fixed facts, prompt panels, multiple engines and competing pages. A small source-reading test alone cannot validate organic discovery. |
| 2. Define and validate GEO measures | [Answer scoring](../pipeline/geo.py) checks citation presence, version, passage support and accuracy. [Referral measures](referrals.md) report covered and unclassified traffic. | Agree definitions with partners, assess inter-rater agreement and reconcile logged visits. |
| 3. Analyse trends and associations across content and sources | [Weekly evidence](../data/referrals.json) compares three publisher types and two formats under a balanced synthetic probe design. | Replicate with measured answer logs, query mix, retailer coverage and sampling uncertainty. |
| 4. Design, execute and iterate A/B tests | [Trial pipeline](../pipeline/build.py), [predefined decision rule](research-design.md) and [three commercial decisions](../data/experiment.json). | Check power and exposure, preregister the retailer trial, then test on consented, eligible traffic. |
| 5. Lead technical delivery and report to the LMC | [Milestones and reporting cadence](handover.md) and exportable decision briefs. | Report spend, risks, departures from the protocol and adoption at quarterly LMC meetings. |
| 6. Collaborate with academic and company supervisors | [Role allocation and monthly reviews](handover.md). | Agree steering decisions, travel and attendance with the supervisors. |
| 7. Adapt research to results | The monitor's wide interval prompts a new test. The speaker's failed allocation check makes instrumentation the next task. [Trial evidence](../data/experiment.json) | Document the changed hypothesis or design before collecting follow-up outcomes. |
| 8. Deliver independently against objectives and time | [Technical route and acceptance checks](technical-route.md), tested data rebuilds, versioned release. | Track milestones, owner, budget and escalation decisions. |
| 9. Review literature and perform reproducible empirical work | [Methods and sources](research-design.md), [SQL](../sql/daily_arms.sql), [analytical tests](../tests/test_analytics.py). | Secure supervisor review and independent replication from approved source data. |
| 10. Work independently and within both organisations | A running implementation plus [responsibility and acceptance criteria](handover.md) for engineering, brand, retail and academic teams. | Actual joint delivery and team performance need workplace evidence. |
| 11. Seek stakeholder challenge and disseminate results | Review outcomes and notes can travel with the exported brief. The [handover exercise](handover.md) asks a commercial reviewer to identify evidence that would change a decision. | Recruit reviewers, log disagreement, assign actions and confirm closure. |
| 12. Report and present research progress | Commercial brief, interactive visuals and a [research-facing protocol](research-design.md). | Deliver and discuss weekly, monthly and quarterly updates with their intended audiences. |
| 13. Contribute to academic outputs under confidentiality | Research questions, observations and threats to validity form a [short methods note](research-design.md). | Obtain commercial clearance and co-author a publishable paper or presentation where appropriate. |
| 14. Supervise staff on specific tasks where needed | [Publisher, engineer and analyst work packages](handover.md) have explicit decisions and acceptance checks. | Agree delegated tasks and review outputs. Formal line management is outside this job's stated remit. |
| 15. Coordinate small teams | [Pilot stages and owners](handover.md) specify handoffs across commercial, engineering and academic roles. | Schedule people, resolve competing priorities and check closure. |
| 16. Observe university, business, KTP policies and confidentiality | Publicly disclosed specifications, labelled simulated records, browser-local notes and a [private-cloud proposal](handover.md). | Obtain approvals and define retention, publication and partner-specific access terms before real data ingestion. |
| 17. Undertake reasonable additional duties | [Project governance](handover.md) provides the review forum and named decision owners. | Agree the scope, delivery implications and appropriate owner with the project supervisors. |

## Reproduce the evidence

Run the [README commands](../README.md#run-locally) to regenerate the synthetic observations and validate both the statistics and browser state transitions. The [desktop view](desktop.jpg) and [mobile view](mobile.jpg) were captured from the public site.
