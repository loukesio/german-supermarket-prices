"""
German Supermarket Prices — interactive dashboard (DE / EN / EL).

    streamlit run dashboard.py

Reads data/prices.csv (see README.md for sources & caveats).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── design tokens (validated palette) ────────────────────────────────────────
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"
BLUE, BLUE_DARK = "#2a78d6", "#0d366b"
CAT = {"open-prices": "#2a78d6", "dm-website": "#eb6834", "marktguru-offers": "#1baf7a"}

# ── i18n ─────────────────────────────────────────────────────────────────────
I18N = {
"de": {
    "caption": "Offener Datensatz deutscher Supermarktpreise — Open Prices, dm, marktguru. "
               "Die Abdeckung ist unvollständig: ein fehlender Preis bedeutet «keine Daten», nicht «gleicher Preis».",
    "k_prices": "Preise", "k_chains": "Ketten", "k_products": "Produkte",
    "k_comparable": "Vergleichbar (gleiche EAN, 2+ Ketten)",
    "h_cheapest": "Welche Kette ist am häufigsten die günstigste?",
    "c_cheapest": "Bei den {n} Produkten mit derselben EAN in 2+ Ketten. Gleichstände zählen für alle Ketten.",
    "hover_wins": "günstigste bei", "wins_unit": "Produkten",
    "h_explorer": "Ein Produkt über Ketten vergleichen",
    "l_product": "Produkt (EAN in 2+ Ketten)",
    "c_best": "Am günstigsten bei **{best}** (€{bp:.2f}) — {worst} €{wp:.2f} → Unterschied {r:.2f}×.",
    "h_spreads": "Die größten Preisunterschiede",
    "x_spreads": "teuerstes ÷ günstigstes Regal",
    "h_coverage": "Abdeckung nach Kette und Quelle",
    "src_op": "Open Prices (Regal)", "src_dm": "dm (Katalog)", "src_mg": "marktguru (Angebote)",
    "t_table": "Vollständige Datentabelle ({n} Zeilen)",
    "l_filter": "Filter (Name, Kette, Barcode)", "btn_csv": "CSV herunterladen",
    "footer": "Quellen: Open Prices (ODbL) · dm Produktsuche · marktguru Angebote. "
              "Angebotspreise laufen ab — siehe Spalte price_date.",
},
"en": {
    "caption": "Open dataset of German supermarket prices — Open Prices, dm, marktguru. "
               "Coverage is partial: a missing price means “no data”, not “same price”.",
    "k_prices": "Prices", "k_chains": "Chains", "k_products": "Products",
    "k_comparable": "Comparable (same EAN, 2+ chains)",
    "h_cheapest": "Which chain is cheapest most often?",
    "c_cheapest": "Across the {n} products sharing an EAN at 2+ chains. Ties count for every chain.",
    "hover_wins": "cheapest for", "wins_unit": "products",
    "h_explorer": "Compare one product across chains",
    "l_product": "Product (EAN at 2+ chains)",
    "c_best": "Cheapest at **{best}** (€{bp:.2f}) — {worst} €{wp:.2f} → {r:.2f}× difference.",
    "h_spreads": "Biggest price spreads",
    "x_spreads": "priciest ÷ cheapest shelf",
    "h_coverage": "Coverage per chain and source",
    "src_op": "Open Prices (shelf)", "src_dm": "dm (catalog)", "src_mg": "marktguru (offers)",
    "t_table": "Full data table ({n} rows)",
    "l_filter": "Filter (name, chain, barcode)", "btn_csv": "Download CSV",
    "footer": "Sources: Open Prices (ODbL) · dm product search · marktguru offers. "
              "Offer prices expire — see the price_date column.",
},
"el": {
    "caption": "Ανοιχτό dataset τιμών από γερμανικές αλυσίδες — Open Prices, dm, marktguru. "
               "Η κάλυψη είναι μερική: όπου λείπει τιμή σημαίνει «χωρίς δεδομένα», όχι «ίδια τιμή».",
    "k_prices": "Τιμές", "k_chains": "Αλυσίδες", "k_products": "Προϊόντα",
    "k_comparable": "Συγκρίσιμα (ίδιο EAN, 2+ αλυσίδες)",
    "h_cheapest": "Ποια αλυσίδα είναι πιο συχνά η φθηνότερη;",
    "c_cheapest": "Στα {n} προϊόντα με το ίδιο barcode σε 2+ αλυσίδες. Ισοπαλίες μετρούν για όλες.",
    "hover_wins": "φθηνότερη σε", "wins_unit": "προϊόντα",
    "h_explorer": "Σύγκρινε ένα προϊόν ανά αλυσίδα",
    "l_product": "Προϊόν (EAN σε 2+ αλυσίδες)",
    "c_best": "Φθηνότερα στο **{best}** (€{bp:.2f}) — {worst} €{wp:.2f} → διαφορά {r:.2f}×.",
    "h_spreads": "Οι μεγαλύτερες διαφορές τιμής",
    "x_spreads": "ακριβότερο ÷ φθηνότερο ράφι",
    "h_coverage": "Κάλυψη ανά αλυσίδα και πηγή",
    "src_op": "Open Prices (ράφι)", "src_dm": "dm (κατάλογος)", "src_mg": "marktguru (προσφορές)",
    "t_table": "Πλήρης πίνακας δεδομένων ({n} γραμμές)",
    "l_filter": "Φίλτρο (όνομα, αλυσίδα, barcode)", "btn_csv": "Λήψη CSV",
    "footer": "Πηγές: Open Prices (ODbL) · dm product search · marktguru offers. "
              "Οι τιμές προσφορών λήγουν — δες τη στήλη price_date.",
},
}
LANGS = {"de": "🇩🇪 Deutsch", "en": "🇬🇧 English", "el": "🇬🇷 Ελληνικά"}

st.set_page_config(page_title="German Supermarket Prices", page_icon="🛒",
                   layout="wide")

title_col, lang_col = st.columns([4, 1])
with lang_col:
    lang = st.selectbox("Language", list(LANGS), index=0,
                        format_func=LANGS.get, label_visibility="collapsed")
t = lambda k, **kw: I18N[lang][k].format(**kw)
CAT_LABEL = {"open-prices": t("src_op"), "dm-website": t("src_dm"),
             "marktguru-offers": t("src_mg")}

with title_col:
    st.title("🛒 German Supermarket Prices")
st.caption(t("caption"))


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
    return df


df = load()
ean_df = df[df.ean_barcode != ""]
counts = ean_df.groupby("ean_barcode")["retailer"].nunique()
multi_eans = counts[counts >= 2].index
cmp_df = ean_df[ean_df.ean_barcode.isin(multi_eans)]

c1, c2, c3, c4 = st.columns(4)
c1.metric(t("k_prices"), f"{len(df):,}")
c2.metric(t("k_chains"), df.retailer.nunique())
c3.metric(t("k_products"), df.product_name.nunique())
c4.metric(t("k_comparable"), len(multi_eans))

# ── 1 · cheapest-chain scoreboard ────────────────────────────────────────────
st.subheader(t("h_cheapest"))
st.caption(t("c_cheapest", n=len(multi_eans)))
mins = cmp_df.groupby("ean_barcode")["price_eur"].transform("min")
wins = (cmp_df[cmp_df.price_eur == mins].groupby("retailer")["ean_barcode"]
        .nunique().sort_values())
fig = go.Figure(go.Bar(
    x=wins.values, y=wins.index, orientation="h",
    marker_color=BLUE, width=0.55,
    text=wins.values, textposition="outside", textfont=dict(color=INK2),
    hovertemplate="%{y}: " + t("hover_wins") + " %{x} " + t("wins_unit") + "<extra></extra>"))
st.plotly_chart(style(fig, height=60 + 32 * len(wins)), use_container_width=True)

# ── 2 · product explorer ─────────────────────────────────────────────────────
st.subheader(t("h_explorer"))
name_of = (cmp_df.sort_values("price_eur").groupby("ean_barcode")["product_name"].first())
spread = cmp_df.groupby("ean_barcode")["price_eur"].agg(["min", "max", "count"])
spread["label"] = name_of
options = spread.sort_values("count", ascending=False)
choice = st.selectbox(t("l_product"), options.index,
                      format_func=lambda e: f"{options.loc[e,'label'][:70]}  ·  {e}")
sel = cmp_df[cmp_df.ean_barcode == choice].sort_values("price_eur", ascending=False)
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
    st.caption(t("c_best", best=best.retailer, bp=best.price_eur,
                 worst=worst.retailer, wp=worst.price_eur,
                 r=worst.price_eur / best.price_eur))

# ── 3 · biggest spreads ──────────────────────────────────────────────────────
st.subheader(t("h_spreads"))
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
fig.update_xaxes(title_text=t("x_spreads"), title_font_color=MUTED)
st.plotly_chart(style(fig, height=60 + 32 * len(top)), use_container_width=True)

# ── 4 · coverage per retailer & source ───────────────────────────────────────
st.subheader(t("h_coverage"))
cov = df.groupby(["retailer", "source"]).size().unstack(fill_value=0)
cov = cov.loc[cov.sum(axis=1).sort_values().index].tail(10)
fig = go.Figure()
for src in ["open-prices", "dm-website", "marktguru-offers"]:
    if src in cov.columns:
        fig.add_bar(x=cov[src], y=cov.index, orientation="h",
                    name=CAT_LABEL[src], marker_color=CAT[src], width=0.55,
                    hovertemplate="%{y} · " + CAT_LABEL[src] + ": %{x}<extra></extra>")
fig.update_layout(barmode="stack")
fig.update_traces(marker_line=dict(color="white", width=2))
st.plotly_chart(style(fig, height=60 + 32 * len(cov), showlegend=True),
                use_container_width=True)

# ── 5 · table view ───────────────────────────────────────────────────────────
with st.expander(t("t_table", n=f"{len(df):,}")):
    q = st.text_input(t("l_filter"))
    view = df
    if q:
        m = view.apply(lambda r: q.lower() in str(r.values).lower(), axis=1)
        view = view[m]
    st.dataframe(view, use_container_width=True, height=420)
    st.download_button(t("btn_csv"), view.to_csv(index=False), "prices.csv", "text/csv")

st.caption(t("footer"))
