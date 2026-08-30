"""
German Supermarket Prices — interactive dashboard.

    streamlit run dashboard.py

Reads data/prices.csv (see README.md for sources & caveats).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── design tokens (validated palette — see repo history) ─────────────────────
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"
BLUE, BLUE_DARK = "#2a78d6", "#0d366b"          # sequential hue + emphasis step
CAT = {"open-prices": "#2a78d6", "dm-website": "#eb6834", "marktguru-offers": "#1baf7a"}
CAT_LABEL = {"open-prices": "Open Prices (ράφι)", "dm-website": "dm (κατάλογος)",
             "marktguru-offers": "marktguru (προσφορές)"}

st.set_page_config(page_title="German Supermarket Prices", page_icon="🛒",
                   layout="wide")


def style(fig, height=380, showlegend=False):
    fig.update_layout(
        height=height, showlegend=showlegend,
        font=dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif",
                  color=INK, size=13),
        paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10),
        bargap=0.35, barcornerradius=4,
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font_color=INK),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=BASELINE, linecolor=BASELINE,
                     tickfont=dict(color=MUTED, size=12))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=BASELINE, linecolor=BASELINE,
                     tickfont=dict(color=MUTED, size=12))
    return fig


@st.cache_data
def load():
    df = pd.read_csv("data/prices.csv", dtype={"ean_barcode": str})
    df["ean_barcode"] = df["ean_barcode"].fillna("")
    df["is_offer"] = df["source"] == "marktguru-offers"
    return df


df = load()

# products comparable across chains (same EAN at 2+ retailers)
ean_df = df[df.ean_barcode != ""]
counts = ean_df.groupby("ean_barcode")["retailer"].nunique()
multi_eans = counts[counts >= 2].index
cmp_df = ean_df[ean_df.ean_barcode.isin(multi_eans)]

st.title("🛒 German Supermarket Prices")
st.caption("Ανοιχτό dataset τιμών από γερμανικές αλυσίδες — Open Prices, dm, marktguru. "
           "Η κάλυψη είναι μερική: όπου λείπει τιμή σημαίνει «χωρίς δεδομένα», όχι «ίδια τιμή».")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Τιμές", f"{len(df):,}")
c2.metric("Αλυσίδες", df.retailer.nunique())
c3.metric("Προϊόντα", df.product_name.nunique())
c4.metric("Συγκρίσιμα (ίδιο EAN, 2+ αλυσίδες)", len(multi_eans))

# ── 1 · cheapest-chain scoreboard ────────────────────────────────────────────
st.subheader("Ποια αλυσίδα είναι πιο συχνά η φθηνότερη;")
st.caption(f"Στα {len(multi_eans)} προϊόντα με το ίδιο barcode σε 2+ αλυσίδες. "
           "Ισοπαλίες μετρούν για όλες τις αλυσίδες.")
mins = cmp_df.groupby("ean_barcode")["price_eur"].transform("min")
wins = (cmp_df[cmp_df.price_eur == mins].groupby("retailer")["ean_barcode"]
        .nunique().sort_values())
fig = go.Figure(go.Bar(
    x=wins.values, y=wins.index, orientation="h",
    marker_color=BLUE, width=0.55,
    text=wins.values, textposition="outside", textfont=dict(color=INK2),
    hovertemplate="%{y}: φθηνότερη σε %{x} προϊόντα<extra></extra>"))
st.plotly_chart(style(fig, height=60 + 32 * len(wins)), use_container_width=True)

# ── 2 · product explorer ─────────────────────────────────────────────────────
st.subheader("Σύγκρινε ένα προϊόν ανά αλυσίδα")
name_of = (cmp_df.sort_values("price_eur").groupby("ean_barcode")["product_name"].first())
spread = (cmp_df.groupby("ean_barcode")["price_eur"].agg(["min", "max", "count"]))
spread["label"] = name_of
options = spread.sort_values("count", ascending=False)
choice = st.selectbox("Προϊόν (EAN σε 2+ αλυσίδες)", options.index,
                      format_func=lambda e: f"{options.loc[e,'label'][:70]}  ·  {e}")
sel = (cmp_df[cmp_df.ean_barcode == choice]
       .sort_values("price_eur", ascending=False))
colors = [BLUE_DARK if p == sel.price_eur.min() else BLUE for p in sel.price_eur]
fig = go.Figure(go.Bar(
    x=sel.price_eur, y=sel.retailer, orientation="h",
    marker_color=colors, width=0.55,
    text=[f"€{p:.2f}" for p in sel.price_eur], textposition="outside",
    textfont=dict(color=INK2),
    customdata=sel[["price_date", "source"]],
    hovertemplate="%{y}: €%{x:.2f} · %{customdata[0]} · %{customdata[1]}<extra></extra>"))
fig.update_xaxes(title_text="€", title_font_color=MUTED)
st.plotly_chart(style(fig, height=80 + 34 * len(sel)), use_container_width=True)
best = sel.loc[sel.price_eur.idxmin()]
worst = sel.loc[sel.price_eur.idxmax()]
if best.price_eur < worst.price_eur:
    st.caption(f"Φθηνότερα στο **{best.retailer}** (€{best.price_eur:.2f}) — "
               f"{worst.retailer} €{worst.price_eur:.2f} → διαφορά "
               f"{worst.price_eur / best.price_eur:.2f}×.")

# ── 3 · biggest spreads ──────────────────────────────────────────────────────
st.subheader("Οι μεγαλύτερες διαφορές τιμής")
sp = spread[spread["min"] > 0].copy()
sp["ratio"] = sp["max"] / sp["min"]
top = sp[sp.ratio > 1.01].sort_values("ratio").tail(12)
fig = go.Figure(go.Bar(
    x=top.ratio, y=[l[:48] for l in top.label], orientation="h",
    marker_color=BLUE, width=0.55,
    text=[f"{r:.1f}×" for r in top.ratio], textposition="outside",
    textfont=dict(color=INK2),
    customdata=top[["min", "max"]],
    hovertemplate="%{y}<br>€%{customdata[0]:.2f} → €%{customdata[1]:.2f} (%{x:.2f}×)<extra></extra>"))
fig.update_xaxes(title_text="ακριβότερο ÷ φθηνότερο ράφι", title_font_color=MUTED)
st.plotly_chart(style(fig, height=60 + 32 * len(top)), use_container_width=True)

# ── 4 · coverage per retailer & source ───────────────────────────────────────
st.subheader("Κάλυψη ανά αλυσίδα και πηγή")
cov = (df.groupby(["retailer", "source"]).size().unstack(fill_value=0))
cov = cov.loc[cov.sum(axis=1).sort_values().index].tail(10)
fig = go.Figure()
for src in ["open-prices", "dm-website", "marktguru-offers"]:
    if src in cov.columns:
        fig.add_bar(x=cov[src], y=cov.index, orientation="h",
                    name=CAT_LABEL[src], marker_color=CAT[src], width=0.55,
                    hovertemplate="%{y} · " + CAT_LABEL[src] + ": %{x}<extra></extra>")
fig.update_layout(barmode="stack")
fig.update_traces(marker_line=dict(color="white", width=2))   # 2px spacer between segments
st.plotly_chart(style(fig, height=60 + 32 * len(cov), showlegend=True),
                use_container_width=True)

# ── 5 · table view (accessibility relief + raw access) ───────────────────────
with st.expander(f"Πλήρης πίνακας δεδομένων ({len(df):,} γραμμές)"):
    q = st.text_input("Φίλτρο (όνομα, αλυσίδα, barcode)")
    view = df
    if q:
        m = view.apply(lambda r: q.lower() in str(r.values).lower(), axis=1)
        view = view[m]
    st.dataframe(view, use_container_width=True, height=420)
    st.download_button("Λήψη CSV", view.to_csv(index=False), "prices.csv", "text/csv")

st.caption("Πηγές: Open Prices (ODbL) · dm product search · marktguru offers. "
           "Offer-τιμές λήγουν — δες τη στήλη price_date.")
