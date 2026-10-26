"""Synthetic blockchain wallet network explorer; no real-world attribution."""
import pandas as pd
import streamlit as st
from src.analyze import ROOT, analyze, load_seeds, load_transfers

st.set_page_config(page_title="Wallet Network Analysis", page_icon="🔗", layout="wide")
st.title("Blockchain Wallet Network Analysis")
st.caption("Synthetic transaction network · Directed flows · Explainable review indicators")
st.warning("Educational demonstration only. Graph proximity does not imply wrongdoing, sanctions exposure, or common ownership.")

try:
    transfers = load_transfers(ROOT / "data/transfers.csv")
    seeds = load_seeds(ROOT / "data/seed_labels.csv")
    metrics = analyze(transfers, seeds)
except (OSError, ValueError) as exc:
    st.error(f"Input validation failed: {exc}")
    st.stop()

tx = pd.DataFrame(transfers)
wallets = pd.DataFrame(metrics)
st.sidebar.header("Network filters")
wallet_ids = wallets["wallet_id"].tolist()
selected = st.sidebar.multiselect("Wallets to display", wallet_ids, default=wallet_ids)
priority = st.sidebar.slider("Minimum demo priority score", 0, 50, 0, 5)
shown = wallets[wallets["wallet_id"].isin(selected) & (wallets["demo_priority_score"] >= priority)].copy()

a, b, c, d = st.columns(4)
a.metric("Wallets in full graph", len(wallets))
b.metric("Transfers", len(tx))
c.metric("Synthetic labeled seeds", len(seeds))
d.metric("Wallets matching filters", len(shown))

st.subheader("Wallet activity and indicators")
st.dataframe(shown.rename(columns={
    "wallet_id": "Wallet", "incoming_transfers": "Incoming tx",
    "outgoing_transfers": "Outgoing tx", "incoming_usd": "Incoming USD",
    "outgoing_usd": "Outgoing USD", "unique_outgoing_counterparties": "Distinct outgoing peers",
    "hops_to_demo_seed": "Directed hops to seed", "demo_priority_score": "Demo priority",
    "review_note": "Review note"
}), use_container_width=True, hide_index=True)
if not shown.empty:
    st.download_button("Export filtered wallet metrics (CSV)", shown.to_csv(index=False),
                       "synthetic_wallet_metrics.csv", "text/csv")
    left, right = st.columns(2)
    with left:
        st.subheader("Outgoing transfer volume")
        st.bar_chart(shown.set_index("wallet_id")["outgoing_usd"])
    with right:
        st.subheader("Directed transfer counts")
        st.bar_chart(shown.set_index("wallet_id")[["incoming_transfers", "outgoing_transfers"]])

st.subheader("Directed transaction network")
st.caption("Arrows represent sender → recipient. Node colors indicate only the synthetic seed or graph proximity.")
if selected:
    # Generate a Graphviz DOT graph without extra Python dependencies.
    def quote(value):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    nodes = set(shown["wallet_id"])
    dot = ['digraph Wallets {', 'rankdir=LR;', 'graph [bgcolor="transparent"];',
           'node [shape=circle, style=filled, fontname="Arial"];']
    for row in shown.itertuples():
        color = "#f0a35a" if row.wallet_id in seeds else (
            "#a9d6ef" if row.hops_to_demo_seed is not None else "#dbe2e8")
        dot.append(f'{quote(row.wallet_id)} [fillcolor="{color}"];')
    for transfer in transfers:
        if transfer["from_wallet"] in nodes and transfer["to_wallet"] in nodes:
            dot.append(f'{quote(transfer["from_wallet"])} -> {quote(transfer["to_wallet"])} '
                       f'[label="{transfer["tx_id"]}"];')
    dot.append("}")
    st.graphviz_chart("\n".join(dot), use_container_width=True)
else:
    st.info("Select wallets to display the network.")

st.subheader("Wallet investigation preview")
if not shown.empty:
    wallet = st.selectbox("Inspect wallet", shown["wallet_id"].tolist())
    record = next(row for row in metrics if row["wallet_id"] == wallet)
    st.write(f"**Review indicator:** {record['review_note']} · **Demo priority:** {record['demo_priority_score']}")
    related = tx[(tx["from_wallet"] == wallet) | (tx["to_wallet"] == wallet)]
    st.dataframe(related, use_container_width=True, hide_index=True)
    st.info("Directed graph distance is structural only: it does not establish time-ordered fund flows or wallet ownership.")

with st.expander("Methodology and limitations"):
    st.markdown("""
- Directed edges connect sender to recipient.
- Hops to the synthetic seed are calculated upstream by shortest directed path.
- Scores are arbitrary demo prioritization values: seed 50, one hop 25, two hops 10, otherwise 0.
- This is **not** a calibrated risk model, sanctions screen, tracing engine, or compliance decision.
- Wallet addresses, transactions, labels and USD values are fabricated.
""")
