import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze import ROOT, analyze, load_seeds, load_transfers

class WalletAnalyticsTests(unittest.TestCase):
    def test_fixture(self):
        rows = analyze(load_transfers(ROOT / "data/transfers.csv"),
                       load_seeds(ROOT / "data/seed_labels.csv"))
        by_id = {row["wallet_id"]: row for row in rows}
        self.assertEqual(len(by_id), 9)
        self.assertEqual(by_id["W_D"]["hops_to_demo_seed"], 0)
        self.assertEqual(by_id["W_C"]["hops_to_demo_seed"], 1)
        self.assertEqual(by_id["W_B"]["hops_to_demo_seed"], 2)
        self.assertEqual(by_id["W_A"]["hops_to_demo_seed"], 3)
        self.assertIsNone(by_id["W_I"]["hops_to_demo_seed"])
        self.assertEqual(by_id["W_F"]["unique_outgoing_counterparties"], 3)

    def test_empty_graph(self):
        self.assertEqual(analyze([], set()), [])

    def test_cycle_terminates_and_finds_shortest_hops(self):
        tx = [{"from_wallet": a, "to_wallet": b, "amount_usd": 1}
              for a, b in [("A", "B"), ("B", "A"), ("B", "SEED")]]
        rows = {r["wallet_id"]: r for r in analyze(tx, {"SEED"})}
        self.assertEqual(rows["B"]["hops_to_demo_seed"], 1)
        self.assertEqual(rows["A"]["hops_to_demo_seed"], 2)

    def test_unreachable_wallet_has_no_seed_path(self):
        tx = [{"from_wallet": "X", "to_wallet": "Y", "amount_usd": 5}]
        rows = {r["wallet_id"]: r for r in analyze(tx, {"SEED"})}
        self.assertIsNone(rows["X"]["hops_to_demo_seed"])
        self.assertEqual(rows["X"]["demo_priority_score"], 0)

    def test_duplicate_transfer_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transfers.csv"
            header = "tx_id,timestamp,from_wallet,to_wallet,amount_usd\n"
            row = "T,2026-01-01T12:00:00,A,B,100\n"
            path.write_text(header + row + row, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate transaction ID"):
                load_transfers(path)

    def test_non_demo_seed_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labels.csv"
            path.write_text("wallet_id,seed_category,source\nW1,TEST,EXTERNAL\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Only synthetic"):
                load_seeds(path)

if __name__ == "__main__":
    unittest.main()
