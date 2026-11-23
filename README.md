# Shelf Evidence

An independent portfolio project by Rongsen Zhang for the University of Bath and Flixmedia Data Product Analyst KTP (CC14066). Version 1.0 explores which retail product-page revisions deserve a controlled pilot. It connects source-grounded shopping answers, referral measurement and an independently assessed shopper experiment.

**[Open the interactive workbench](https://rongsenzhang.github.io/shelf-evidence-lab/)** · [Job responsibilities and evidence](docs/role-evidence.md) · [Business and competitors](docs/market.md) · [Technical route](docs/technical-route.md)

## A three-minute review

1. From the overview, open the **Arc One headphones** case. Compare a shopping question across old and revised copy. Inspect the source passage and whether the quoted text supports the answer.
2. Open **Traffic & citations** for source coverage, tagged visits and differences between publisher and content formats. Then open **Shopper experiment**. The simulated rate moves from 726/7,460 to 876/7,556. The estimated +1.86 percentage point difference has a 95% interval of +0.87 to +2.85. The lower bound clears the prespecified +0.50-point pilot gate.
3. Switch to **Tide Mini speaker**. Its apparent gain of +2.14 points fails the allocation check. Record the decision and export the handoff. The **Forma 27 monitor** shows a different reason to hold: its interval spans commercially important gains and losses.
4. Open **Controlled AI run** from the overview for a separate real observation. Two fresh readers received different analyst-written cards based on Logitech's UK business-keyboard specifications. Adding the box contents and device limit gave the reader evidence to answer two additional questions. Both readers abstained on waterproofing. Inspect the exact inputs and outputs.

## What was measured

| Evidence | Origin and interpretation |
| --- | --- |
| Product-copy comparisons | 3 fictional SKUs, 12 questions, 48 authored answer fixtures. The scoring code checks quotes, version and approved facts. |
| Citation and referral panel | 1,152 seeded citation probes plus synthetic channel labels on the same 26,140 simulated sessions. Measures coverage, tagged visits and descriptive associations. |
| Shopper experiments | Three independent 28-day simulated trials. Each includes assigned sessions with no subsequent event. Outcomes include engagement, add-to-cart and purchase. |
| Observed AI source-reading exercise | A public Logitech specification, two independent reader contexts, four questions per card, a single captured batch per card. The exercise tests answerability with supplied sources. Live search visibility and sales outcomes require a retailer pilot. |

All public trial numbers are synthetic. Customer, product and brand names in the three trials are fictional. Logitech is identified only as the source for the separate controlled exercise. The project is independently produced and no partner endorsement, internal API access, customer records or licensed model feed is implied.

## Run locally

Python 3.9+ provides the analysis and preview server. Node.js 18+ runs the optional UI smoke suite. There are no package installations or credentials.

```sh
python3 pipeline/build.py
python3 pipeline/geo.py
python3 pipeline/referrals.py
python3 -m unittest discover -s tests -v
node tests/frontend-smoke.cjs
python3 -m http.server 8000
```

Open [localhost:8000](http://localhost:8000/) from the same computer. The browser fetches four versioned JSON files. Draft reviews are kept in this browser's local storage and can be exported as Markdown. The captured model responses are frozen observations. Replaying the page leaves them intact.

## Research and transfer

- [Experimental design and identification](docs/research-design.md)
- [Referral attribution and source/format trends](docs/referrals.md)
- [Data contract, SQL and reproduction](pipeline/README.md)
- [Partner pilot, governance and handover exercise](docs/handover.md)
- [Evidence map across the 17 responsibilities](docs/role-evidence.md)
- [Official vacancy and role attachment](https://www.bath.ac.uk/jobs/Vacancy.aspx?ref=CC14066)
