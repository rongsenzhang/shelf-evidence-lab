# From a portfolio study to a partner pilot

The reporting cadence and development commitments below follow Bath's job description. The six delivery stages are a proposed plan for the 18-month partnership. The partners would agree access, budget and publication rights. The public v1.0 uses fictional trials and independently gathered public evidence. [University of Bath role](https://www.bath.ac.uk/jobs/Vacancy.aspx?ref=CC14066) · [Job description and person specification](https://www.bath.ac.uk/jobs/Upload/vacancies/files/30288/Flixmedia%20JD.doc)

## Who decides what

| Owner | Decision or deliverable |
| --- | --- |
| KTP Associate | Own the hypothesis register, prioritised backlog, analysis code, spend review, decision record and training. Supervise contributors on specific project tasks. The role carries no formal line-management responsibility. Escalate blocked access or unreliable measurement to both supervisors. |
| Company product lead | Select the client problem, agree the smallest commercially useful lift, allocate engineering time and own the roadmap after handover. |
| Retailer and brand content owners | Confirm destination eligibility, in-stock period, page treatment and claim wording. The retailer owns placement and change control. The brand verifies specifications and approval to publish. |
| Company data engineer | Map source fields, diagnose logging gaps, own access and refresh alerts, and reconcile assignment and outcome counts. |
| Bath academic supervisor | Challenge identification, power, model evaluation and interpretation. Review the protocol and proposed research output. |
| Local Management Committee (LMC) | Review delivery, budget, risks and commercial adoption with the company, the university and Innovate UK. Record decisions to continue, revise scope or stop a pilot. |

## Reporting and development

| When | Output |
| --- | --- |
| Weekly | The Associate provides a progress update covering completed work, new evidence, current risks and the decision needed next. |
| Monthly | The company and academic supervisors review the work with the Associate. Check milestones, spend and research quality, then record owners and due dates for agreed actions. |
| Quarterly | The Associate presents the project report to the LMC, including Innovate UK representation. Bring the current workplan, budget position, risks, pilot results and decisions requiring committee support. |
| Across the appointment | Schedule the two residential KTP training modules. Allow for travel to Bath for up to 15% of working time, and coordinate university visits with methods reviews, research seminars and knowledge-transfer work. |

## Proposed 18-month delivery

| Months | Work and decision point |
| --- | --- |
| 1–3 | Shadow a brand content manager and a retailer analyst. Agree one recurring decision, data rights, minimum worthwhile effect, outcome window and baseline. Proceed after both owners can reconcile counts for one SKU and reproduce its current copy. |
| 4–6 | Map the source tables and publish a data dictionary. Version content and register the prompt panel. Independently double-score a sample of answer claims, resolve disagreements and record the scoring rule. Demonstrate one complete decision using a historical window. |
| 7–9 | Run an A/A trial to catch assignment and event discrepancies. Estimate traffic needs and register a pilot. Agree the operational fallback if the revision fails to render or a claim is unsupported. |
| 10–12 | Run the fixed-horizon pilot. Test the proposed edit in a low-risk category. Check authority for claims, page load, allocation and event coverage. Publish the pilot readout with the retailer's decision and named next owner. |
| 13–15 | Test transfer with a second retailer, device mix or category. Compare accuracy, incremental basket additions and cost per edited SKU. Run a staff workshop using both inconclusive and invalid experiments. |
| 16–18 | Ask a company analyst to run the workflow unaided. Transfer permissions, refresh responsibility and issue triage. Present a costed adoption decision and a methods note suitable for academic review under agreed disclosure terms. |

## Proposed BigQuery integration

Flixmedia describes an Analytics Hub service that provides BigQuery access to datasets including product URLs, traffic, devices, videos and hotspots. The product page does not publish a row-level contract for experiment assignment, order linkage or answer-engine traces. Establish those with the data owners before choosing the production estimand. [Measure Effect API FAQ](https://www.flixmedia.com/measure-optimise-content) · [Google Cloud sharing](https://docs.cloud.google.com/bigquery/docs/analytics-hub-introduction)

| Input | Proposed handling | Acceptance check |
| --- | --- | --- |
| Catalogue and assets | Keep SKU, retailer, locale, destination URL, approved specification, page-version hash and effective time. Preserve prior revisions. | An analyst can identify the exact version in each arm on the experiment date. |
| Shopper events | In a private project, map the authorised feed to assignment, content exposure, add-to-cart and purchase facts. Retain zero-event assignments. Use distinct event IDs for replay safety, a documented late-arrival window and a dated snapshot for each decision. | Assignment totals reconcile to the source log. Counts reconcile by day, device and arm. A duplicate delivery changes no outcome. |
| Answer evidence | Log query, locale, retrieval conditions, model identifier, collection time, response, source URLs, fact-check and human reviewer. Store licensed or sensitive material in the private project. | A second reviewer can inspect the cited passage and distinguish an unsupported claim from an unavailable answer. |
| Reporting | Publish an authorised aggregate view partitioned or filtered by reporting date. A private service account reads it for the internal decision tool. Keep browser code free of cloud credentials. | Reconcile a frozen sample to the local SQL analysis. Enforce brand-scoped query access before serving any client. [BigQuery authorised views](https://docs.cloud.google.com/bigquery/docs/create-authorized-views) |

BigQuery client access, model collection and production monitoring are partner-pilot work. The publicly reproducible route uses Python and local SQLite. To check the evidence from the repository root, generate a new snapshot in a temporary directory and compare it with the committed one.

```sh
study_tmp=$(mktemp -d)
python3 pipeline/build.py --output "$study_tmp/experiment.json" --export-csv "$study_tmp/sessions.csv"
cmp data/experiment.json "$study_tmp/experiment.json"
```

## Fifteen-minute handover exercise

Give a commercial colleague the three fictional cases and ask them to choose which action to take with one content-editing slot. Have them read the control and treatment counts aloud, identify the primary outcome and explain what a percentage point means to a brand manager.

| Case | Expected judgement and evidence |
| --- | --- |
| Headphones | Advance to a second pilot. The basket lift is +1.86 percentage points, with a lower 95% bound of +0.87 points above the +0.5-point hurdle. Validate transfer before a network-wide rollout. |
| Monitor | Retain the control and design a sufficiently powered follow-up. The estimate is +0.31 points and the 95% interval spans –1.42 to +2.05. Both a loss and a worthwhile gain remain plausible. |
| Speaker | Withhold any efficacy recommendation. Its attractive +2.14-point estimate accompanies a failed allocation check. Ask engineering to reconcile variant assignment against logged traffic by day and device. |

The exercise passes when the colleague can explain the two different reasons to hold a rollout, name the evidence that would change each decision and reproduce the figures from the saved snapshot. Record their decision and the next accountable role. [Trial evidence](../data/experiment.json) · [Research protocol](research-design.md)
