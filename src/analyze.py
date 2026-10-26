"""Synthetic directed wallet-flow analysis; no real-world attribution."""
import csv
import json
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"tx_id", "timestamp", "from_wallet", "to_wallet", "amount_usd"}

def load_transfers(path):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not FIELDS.issubset(reader.fieldnames or []):
            raise ValueError("Missing required transaction columns")
        rows = list(reader)
    seen = set()
    for row in rows:
        if any(not row.get(k) for k in FIELDS):
            raise ValueError("Missing transaction value")
        if row["tx_id"] in seen:
            raise ValueError("Duplicate transaction ID")
        seen.add(row["tx_id"])
        if row["from_wallet"] == row["to_wallet"]:
            raise ValueError("Self-transfers excluded from this demo")
        datetime.fromisoformat(row["timestamp"])
        row["amount_usd"] = float(row["amount_usd"])
        if not 0 < row["amount_usd"] < float("inf"):
            raise ValueError("Invalid amount")
    return rows

def load_seeds(path):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not {"wallet_id", "seed_category", "source"}.issubset(reader.fieldnames or []):
            raise ValueError("Missing seed columns")
        rows = list(reader)
    if any(not all(row.values()) for row in rows):
        raise ValueError("Missing seed value")
    if any(row["source"] != "DEMO_ONLY" for row in rows):
        raise ValueError("Only synthetic demo seed labels are permitted")
    return {row["wallet_id"] for row in rows}

def analyze(transfers, seeds):
    """Calculate descriptive directed graph metrics and seed reachability."""
    outgoing = defaultdict(set)
    inbound_count = defaultdict(int)
    outbound_count = defaultdict(int)
    inbound_usd = defaultdict(float)
    outbound_usd = defaultdict(float)
    wallets = set(seeds)
    for tx in transfers:
        source, dest, amount = tx["from_wallet"], tx["to_wallet"], tx["amount_usd"]
        wallets.update((source, dest))
        outgoing[source].add(dest)
        outbound_count[source] += 1
        inbound_count[dest] += 1
        outbound_usd[source] += amount
        inbound_usd[dest] += amount
    # Reverse adjacency: how many directed transfer hops a wallet is upstream
    # of a labeled synthetic seed? Reachability is NOT proof of illicit activity.
    upstream = defaultdict(set)
    for source, destinations in outgoing.items():
        for dest in destinations:
            upstream[dest].add(source)
    hops = {seed: 0 for seed in seeds}
    queue = deque(sorted(seeds))
    while queue:
        node = queue.popleft()
        for parent in sorted(upstream[node]):
            if parent not in hops:
                hops[parent] = hops[node] + 1
                queue.append(parent)
    results = []
    for wallet in sorted(wallets):
        distance = hops.get(wallet)
        # Demo prioritization points are intentionally arbitrary and not probabilities.
        score = 50 if wallet in seeds else (25 if distance == 1 else (10 if distance == 2 else 0))
        results.append({
            "wallet_id": wallet,
            "incoming_transfers": inbound_count[wallet],
            "outgoing_transfers": outbound_count[wallet],
            "incoming_usd": round(inbound_usd[wallet], 2),
            "outgoing_usd": round(outbound_usd[wallet], 2),
            "unique_outgoing_counterparties": len(outgoing[wallet]),
            "hops_to_demo_seed": distance,
            "demo_priority_score": score,
            "review_note": ("SYNTHETIC_SEED" if wallet in seeds else
                            "UPSTREAM_CONNECTION" if distance is not None else "NO_SEED_PATH")
        })
    return results

def main():
    records = analyze(load_transfers(ROOT / "data/transfers.csv"),
                      load_seeds(ROOT / "data/seed_labels.csv"))
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    (output / "wallet_summary.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Analyzed {len(records)} synthetic wallets")

if __name__ == "__main__":
    main()
