# Blockchain Wallet Risk Analysis

A reproducible **Python + SQL** blockchain intelligence portfolio demonstration using **entirely fabricated wallet transfers**. The project models directed transaction relationships, summarizes wallet activity, and measures graph distance to a **synthetic** review seed. It does not use real wallet addresses or real sanctions/watchlist information.

## Run the analysis

Requires Python 3.10+ and standard library only:

```bash
python src/analyze.py
python -m unittest discover -s tests -v
```

The pipeline writes `output/wallet_summary.json` with per-wallet activity metrics, directed graph distance to the fabricated seed, and explainable demo prioritization indicators. GitHub Actions runs the tests and pipeline on pushes and pull requests.

## Skills demonstrated
- **Python:** validated CSV ingestion, graph traversal (breadth-first search), aggregation, JSON reporting
- **SQL:** directed wallet in/out flows, transaction counts, USD-denominated totals, distinct counterparties
- **Financial crime analytics:** transparent synthetic watchlist-seed connections and human-review limitations
- **Engineering:** unit tests, reproducible fixtures, automated CI

## Repository layout
- `data/transfers.csv` — invented transfer network
- `data/seed_labels.csv` — explicitly synthetic watchlist seed
- `src/analyze.py` — validation, wallet metrics and directed graph traversal
- `sql/wallet_metrics.sql` — SQLite wallet metrics
- `tests/test_analyze.py` — regression tests
- `docs/methodology.md` — definitions, assumptions, safeguards and limitations
- `.github/workflows/tests.yml` — CI tests and smoke run

## Methodology and limitations

Edges represent sender → recipient. The distance metric measures **upstream directed reachability** to the fabricated seed, not proof that the same funds traveled through the path. Demo priority scores are arbitrary and **not probabilities or compliance determinations**.

There is no on-chain API integration, real-world attribution, customer data, sanctions matching, entity clustering or time-respecting fund tracing. See [methodology](docs/methodology.md) for detail.

## Status

Initial code and automated tests published. An interactive visualization and deployed demo are planned, not yet live.

MIT licensed.
