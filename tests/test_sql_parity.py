import csv
import sqlite3
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze import ROOT, analyze, load_seeds, load_transfers

class SQLParityTests(unittest.TestCase):
    def test_sql_wallet_metrics_match_python(self):
        with (ROOT / "data/transfers.csv").open(newline="", encoding="utf-8") as f:
            raw = list(csv.DictReader(f))
        db = sqlite3.connect(":memory:")
        try:
            db.execute("CREATE TABLE transfers (tx_id TEXT, timestamp TEXT, from_wallet TEXT, to_wallet TEXT, amount_usd REAL)")
            db.executemany("INSERT INTO transfers VALUES (:tx_id,:timestamp,:from_wallet,:to_wallet,:amount_usd)", raw)
            sql = (ROOT / "sql/wallet_metrics.sql").read_text(encoding="utf-8")
            cols = ["wallet_id","incoming_transfers","outgoing_transfers","incoming_usd",
                    "outgoing_usd","unique_outgoing_counterparties"]
            actual = {row[0]: dict(zip(cols,row)) for row in db.execute(sql)}
            expected = {row["wallet_id"]: {k: row[k] for k in cols}
                        for row in analyze(load_transfers(ROOT / "data/transfers.csv"),
                                           load_seeds(ROOT / "data/seed_labels.csv"))}
            self.assertEqual(actual, expected)
        finally:
            db.close()
