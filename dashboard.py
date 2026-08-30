"""
German Supermarket Prices — interactive dashboard (DE / EN / EL).

    streamlit run dashboard.py

Reads data/prices.csv (see README.md for sources & caveats).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── design tokens (validated palette) ────────────────────────────────────────
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"
TEAL, TEAL_DARK = "#0f8f63", "#0b7350"
CAT = {"open-prices": "#1baf7a", "dm-website": "#eb6834", "marktguru-offers": "#4a3aa7"}

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
    "h_search": "Kategorie durchsuchen — alle Produkte, alle Ketten",
    "c_search": "Fläche ∝ 1/Preis — je größer die Kachel, desto billiger das Produkt. Klick auf eine Kette zoomt hinein; Packungsgrößen unterscheiden sich (Hover für Details).",
    "l_search": "Suche, z. B. eier · bio eier · milch · kaffee",
    "no_hits": "Keine Treffer für «{q}».",
    "h_history": "Preisverlauf",
    "c_history": "Echte historische Preise (Open Prices) plus tägliche Schnappschüsse. Punkte = beobachtete Preise.",
    "l_product_h": "Produkt (mit Preishistorie)",
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
    "h_search": "Search a category — every product, every chain",
    "c_search": "Area ∝ 1/price — the bigger the tile, the cheaper the product. Click a chain to zoom in; pack sizes differ (hover for details).",
    "l_search": "Search, e.g. eier · bio eier · milch · kaffee",
    "no_hits": "No matches for “{q}”.",
    "h_history": "Price over time",
    "c_history": "Real historical prices (Open Prices) plus daily snapshots. Dots are observed prices.",
    "l_product_h": "Product (with price history)",
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
    "h_search": "Αναζήτηση κατηγορίας — όλα τα προϊόντα, όλες οι αλυσίδες",
    "c_search": "Εμβαδόν ∝ 1/τιμή — όσο μεγαλύτερο το πλακίδιο, τόσο φθηνότερο το προϊόν. Κλικ σε αλυσίδα για ζουμ· οι συσκευασίες διαφέρουν (hover για λεπτομέρειες).",
    "l_search": "Αναζήτηση, π.χ. eier · bio eier · milch · kaffee",
    "no_hits": "Κανένα αποτέλεσμα για «{q}».",
    "h_history": "Εξέλιξη τιμής στον χρόνο",
    "c_history": "Πραγματικές ιστορικές τιμές (Open Prices) και ημερήσια στιγμιότυπα. Οι κουκκίδες είναι παρατηρημένες τιμές.",
    "l_product_h": "Προϊόν (με ιστορικό τιμών)",
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
# official brand colors, lightness-spread within the red/blue families so
# chains stay distinguishable; names always accompany the marks
BRAND = {
    "REWE":      "#CC071E",   # REWE red (official)
    "Kaufland":  "#F0331F",   # Kaufland scarlet, brightened
    "PENNY":     "#8F0F1E",   # PENNY dark red
    "Rossmann":  "#5C0A14",   # Rossmann cab-sav dark red
    "Nahkauf":   "#E4572E",   # REWE-group, orange-red
    "EDEKA":     "#0B72C0",   # EDEKA blue (official)
    "E-Center":  "#3A8FD1",   # EDEKA family, lighter
    "Lidl":      "#063A75",   # Lidl navy
    "ALDI":      "#0FA7DC",   # ALDI light blue
    "dm":        "#F09500",   # dm golden poppy, deepened
    "Netto":     "#C7B300",   # Netto lemon yellow, deepened for white
    "Norma":     "#D02C2F",
    "Globus":    "#0E8A3E",
    "tegut":     "#E36F1E",
    "HIT":       "#B5122E",
    "CAP-Markt": "#5AA82E",
}
chain_c = lambda c: BRAND.get(c, "#898781")
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
    marker_color=[chain_c(c) for c in wins.index], width=0.55,
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
fig = go.Figure(go.Bar(
    x=sel.price_eur, y=sel.retailer, orientation="h",
    marker_color=[chain_c(c) for c in sel.retailer], width=0.55,
    text=[f"€{p:.2f} ✓" if p == sel.price_eur.min() else f"€{p:.2f}"
          for p in sel.price_eur], textposition="outside",
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

# ── 3 · category search: every product, every chain ─────────────────────────
st.subheader(t("h_search"))
q2 = st.text_input(t("l_search"), value="eier")
if q2.strip():
    hits = df[df.product_name.str.lower().str.contains(q2.strip().lower(), na=False)].copy()
    if not len(hits):
        st.caption(t("no_hits", q=q2))
    else:
        st.caption(t("c_search"))
        hits = hits[hits.price_eur > 0]
        hits["value"] = 1.0 / hits.price_eur          # area ∝ 1/price → cheapest = biggest tile
        hits["tile"] = (hits.product_name.str.slice(0, 40) + " · €"
                        + hits.price_eur.map("{:.2f}".format))
        figt = px.treemap(hits, path=["retailer", "tile"], values="value",
                          color="retailer",
                          color_discrete_map={c: chain_c(c) for c in hits.retailer.unique()},
                          custom_data=["product_name", "price_eur", "source"])
        figt.update_traces(
            marker=dict(cornerradius=4, line=dict(width=2, color="white")),
            textfont=dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif", size=12),
            hovertemplate="<b>%{customdata[0]}</b><br>€%{customdata[1]:.2f} · "
                          "%{customdata[2]}<extra>%{root}</extra>")
        figt.update_layout(height=560, margin=dict(l=4, r=4, t=4, b=4),
                           paper_bgcolor="white",
                           font=dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif",
                                     color=INK))
        st.plotly_chart(figt, use_container_width=True)
        cheap = hits.loc[hits.price_eur.idxmin()]
        st.caption(f"🏆 {cheap.retailer}: {cheap.product_name[:60]} — €{cheap.price_eur:.2f}")

# ── 3b · biggest spreads ─────────────────────────────────────────────────────
st.subheader(t("h_spreads"))
sp = spread[spread["min"] > 0].copy()
sp["ratio"] = sp["max"] / sp["min"]
top = sp[sp.ratio > 1.01].sort_values("ratio").tail(12)
def teal_ramp(vals, lo="#c9ead9", hi="#0b7350"):
    import colorsys
    l, h = [int(lo[i:i+2],16) for i in (1,3,5)], [int(hi[i:i+2],16) for i in (1,3,5)]
    mn, mx = min(vals), max(vals)
    out = []
    for v in vals:
        f = 0.0 if mx == mn else (v - mn) / (mx - mn)
        out.append("#" + "".join(f"{round(a+(b-a)*f):02x}" for a, b in zip(l, h)))
    return out

fig = go.Figure(go.Bar(
    x=top.ratio, y=[l[:48] for l in top.label], orientation="h",
    marker_color=teal_ramp(list(top.ratio)), width=0.55,
    text=[f"{r:.1f}×" for r in top.ratio], textposition="outside",
    textfont=dict(color=INK2),
    customdata=top[["min", "max"]],
    hovertemplate="%{y}<br>€%{customdata[0]:.2f} → €%{customdata[1]:.2f} (%{x:.2f}×)<extra></extra>"))
fig.update_xaxes(title_text=t("x_spreads"), title_font_color=MUTED)
st.plotly_chart(style(fig, height=60 + 32 * len(top)), use_container_width=True)

# ── 4 · price over time ──────────────────────────────────────────────────────
@st.cache_data
def load_history():
    try:
        h = pd.read_csv("data/price_history.csv", dtype={"ean_barcode": str})
    except FileNotFoundError:
        return pd.DataFrame()
    h["ean_barcode"] = h["ean_barcode"].fillna("")
    h["date"] = pd.to_datetime(h["date"], errors="coerce")
    return h.dropna(subset=["date"])

hist = load_history()
if len(hist):
    # global fixed chain→color map (color follows the entity, never the filter)
    st.subheader(t("h_history"))
    st.caption(t("c_history"))
    hh = hist[hist.ean_barcode != ""]
    depth = (hh.groupby("ean_barcode")
               .agg(pts=("price_eur", "size"), days=("date", "nunique"),
                    chains=("retailer", "nunique"), name=("product_name", "first")))
    good = depth[(depth.pts >= 6) & (depth.days >= 3)].sort_values("pts", ascending=False)
    if len(good):
        pick = st.selectbox(t("l_product_h"), good.index,
                            format_func=lambda e: f"{good.loc[e,'name'][:70]}  ·  {e}")
        hsel = hh[hh.ean_barcode == pick].sort_values("date")
        fig = go.Figure()
        for chain, grp in hsel.groupby("retailer"):
            if len(grp) < 2 and len(hsel.retailer.unique()) > 6:
                continue
            fig.add_scatter(x=grp.date, y=grp.price_eur, mode="lines+markers",
                            name=chain, line=dict(width=2, color=chain_c(chain)),
                            marker=dict(size=8, color=chain_c(chain)),
                            hovertemplate=chain + " · %{x|%d.%m.%Y}: €%{y:.2f}<extra></extra>")
        fig.update_yaxes(title_text="€", title_font_color=MUTED, rangemode="tozero")
        st.plotly_chart(style(fig, height=400, showlegend=True), use_container_width=True)

# ── 5 · coverage per retailer & source ───────────────────────────────────────
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
