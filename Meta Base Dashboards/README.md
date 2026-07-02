# Metabase Dashboards

8 dashboards on Metabase Starter connected to BigQuery `final_reporting`.

Structure: `<Dashboard>/<Tab>/queries_and_purpose.md` — every question with its SQL and purpose.

| Dashboard | Tabs |
|---|---|
| Leadership Snapshot | Overview · MTD KPIs · Trends |
| Inventory & Buying | Overview · Aging · Condition & Location · Inventory · Products |
| Retail | KPIs · Trends |
| Ecomm | KPIs · Trends |
| Customers | Overview |
| Supplier & Seller | Overview |
| Shipping & Operations | Overview |
| Marketing | Paid Media · Email (Klaviyo) |

## Filters available
- **Date Range** — all dashboards (Inventory uses single "As of Date" on snapshot_date)
- **Store Location** — all order-based dashboards + Inventory + Customers + Supplier & Seller
- **Sales Channel** — all order-based dashboards + Customers + Supplier & Seller (not applicable to Inventory — unsold stock has no channel; the Products tab bridges this)

## Date comparison
Metabase Starter lacks native "Compare to period" — Number cards use the **Trend** chart type to show change vs previous period. See dashboard_structure.md for the full layout.
