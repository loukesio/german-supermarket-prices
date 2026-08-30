# German Supermarket Prices

An open dataset of grocery and drugstore prices across German retail chains —
ALDI, dm, EDEKA, Kaufland, Lidl, Netto, PENNY, REWE, Rossmann and others.

Current snapshot: **9,109 prices · 16 retailers** (updated 2026-08-30, Göttingen/Berlin/München offer regions).

## Files

| File | Description |
|---|---|
| `data/prices.csv` | One row per (retailer, product): name, EAN barcode where known, category, price in EUR, price date, collection date, source |
| `data/prices.sqlite` | The same data as a standalone SQLite database (table `prices`) |

## Interactive dashboard

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

Cheapest-chain scoreboard, per-product price comparison across chains
(EAN-matched), biggest price spreads, coverage per source, and the full
filterable table. Deployable as-is on
[Streamlit Community Cloud](https://share.streamlit.io) — point it at this
repo and `dashboard.py`.

## Sources

Each row's `source` column states where it came from:

- **`open-prices`** — [Open Prices](https://prices.openfoodfacts.org) by
  [Open Food Facts](https://openfoodfacts.org): crowdsourced shelf prices,
  licensed under the [ODbL](https://opendatacommons.org/licenses/odbl/1-0/).
- **`dm-website`** — dm-drogerie markt's public product search
  (full drugstore assortment with EAN barcodes).
- **`marktguru-offers`** — currently advertised leaflet offers (Angebote)
  aggregated by marktguru.de for the big chains. These are promotional
  prices with limited validity, not regular shelf prices — the `category`
  column marks them with an `Angebot ·` prefix.

## Caveats

- Coverage is partial and uneven: dm is near-complete, discounter chains are
  mostly represented through weekly offers and crowdsourced entries.
- A missing product/chain combination means **no data**, not "same price".
- Offer prices (Angebot rows) expire; check `price_date`.
- Prices are collected for a Berlin postal region where location matters.

## Licence & attribution

The portions derived from Open Prices are © Open Food Facts contributors and
remain under the **ODbL 1.0** — this dataset as a whole is therefore shared
under the same licence (attribution + share-alike). Retailer and product
names belong to their respective owners; prices are factual data collected
from publicly accessible sources for transparency and price-comparison
research. If you are a retailer and want something corrected or removed,
open an issue.
