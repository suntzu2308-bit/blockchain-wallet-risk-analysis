-- SQLite example: import data/transfers.csv as transfers.
-- Directed wallet activity metrics. Labels are synthetic only.
WITH wallet_ids AS (
  SELECT from_wallet AS wallet_id FROM transfers
  UNION
  SELECT to_wallet AS wallet_id FROM transfers
),
incoming AS (
  SELECT to_wallet AS wallet_id, COUNT(*) AS n, SUM(CAST(amount_usd AS REAL)) AS usd
  FROM transfers GROUP BY to_wallet
),
outgoing AS (
  SELECT from_wallet AS wallet_id, COUNT(*) AS n,
         COUNT(DISTINCT to_wallet) AS counterparties,
         SUM(CAST(amount_usd AS REAL)) AS usd
  FROM transfers GROUP BY from_wallet
)
SELECT w.wallet_id, COALESCE(i.n,0) AS incoming_transfers,
       COALESCE(o.n,0) AS outgoing_transfers,
       COALESCE(i.usd,0) AS incoming_usd,
       COALESCE(o.usd,0) AS outgoing_usd,
       COALESCE(o.counterparties,0) AS unique_outgoing_counterparties
FROM wallet_ids w
LEFT JOIN incoming i ON w.wallet_id=i.wallet_id
LEFT JOIN outgoing o ON w.wallet_id=o.wallet_id
ORDER BY w.wallet_id;
