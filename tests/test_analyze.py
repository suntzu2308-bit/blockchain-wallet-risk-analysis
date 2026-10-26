import sys
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
        rows = analyze([], set())
        self.assertEqual(rows, [])

if __name__ == "__main__":
    unittest.main()
