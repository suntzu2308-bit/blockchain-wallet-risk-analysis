# Wallet-flow methodology and safeguards

This project models transfers as a **directed graph** (sender → recipient). It counts transfers, sums USD-denominated illustrative amounts, counts unique outgoing counterparties, and calculates the minimum directed hop distance from each wallet to a single **fabricated** watchlist seed.

The hop calculation traverses incoming edges backward from the labeled seed, so a wallet has distance 1 when it directly sends to the seed. It does **not** claim that value flowed through all intermediary hops, that transactions were temporally ordered, or that the same funds moved along a path.

Demo priority scores: seed = 50; 1 hop upstream = 25; 2 hops = 10; other = 0. These are arbitrary UI-prioritization values, not probability, sanctions status, guilt, or compliance determinations.

## Limitations
- No real addresses, customer data, sanctions lists, chain API, chain analytics vendor, or KYC records
- No token decimals, gas, transaction fees, UTXO, internal calls, bridges, smart-contract attribution, or price conversion
- USD amounts are fabricated and are not actual on-chain settlement values
- No entity clustering, beneficial-ownership inference, probabilistic labels, or temporal path tracing
- Graph connections alone must not be interpreted as criminal involvement

Potential future work: temporal path constraints, label provenance, graph visualization, more robust SQL/Python parity tests, and review case management.
