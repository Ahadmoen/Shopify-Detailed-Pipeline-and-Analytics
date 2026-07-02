# Shopify Detailed Pipeline and Analytics

End-to-end analytics and reporting system for **Mine & Yours** (luxury resale — 5 stores across Vancouver, Toronto, Calgary).

**Stack:** Shopify + Marketing APIs → n8n (Railway) → Google BigQuery → Metabase

---

## Architecture

```
Shopify API ──┐
Meta Ads ─────┤
Google Ads ───┼──► n8n (daily 1PM) ──► BigQuery raw layer ──► Reporting views ──► Metabase (8 dashboards)
Klaviyo ──────┘         │
                        └── Python backfill scripts (Colab) for historical data
```

## Repository Structure

| Folder | Contents |
|---|---|
| `n8n-pipelines/` | n8n workflow JSONs — daily + backfill branches per source |
| `python-backfill-scripts/` | Colab scripts for historical backfills with delete/dedupe patterns |
| `bigquery-views/` | All 9 reporting view definitions (final_reporting dataset) |
| `Meta Base Dashboards/` | Dashboard documentation — every tab, question, query and purpose |

## Data Layer

**Project:** `mine-and-yours-analytics` (us-central1)

**Raw datasets:**
- `raw_shopify` — shopify_orders, shopify_customers, shopify_products, shopify_product_metafields, shopify_refunds
- `raw_marketing` — meta_ads, google_ads, klaviyo_campaigns, klaviyo_lists, klaviyo_campaign_messages, klaviyo_campaign_metrics

**Reporting views (`final_reporting`):**
| View | Purpose |
|---|---|
| fact_orders_v2 | Order-level with COGS, channel, store location, customer id |
| fact_daily_sales_v2 | Daily aggregated sales by channel / store / province |
| fact_product_sales_v2 | Line-item product sales with cost and margin |
| fact_customers_v2 | Customer snapshot with preferred store and channel |
| fact_inventory_v2 | Point-in-time inventory snapshot with aging and location |
| fact_refunds_v2 | Refund records with channel and store mapping |
| fact_marketing_v2 | Meta + Google Ads unioned |
| fact_klaviyo_campaigns_v2 | Email campaign performance |
| fact_seller | Consignment sellers with buyer overlap, store and channel |

## Key Engineering Decisions

1. **Timezone** — all order dates converted `DATE(DATETIME(TIMESTAMP(order_created_at), 'America/Vancouver'))` to match Shopify Admin exactly.
2. **COGS** — Shopify Orders API does not return unit cost; joined from `shopify_products.product_variant_inventory_item_cost` at view level.
3. **Dedup** — raw tables tolerate duplicates; every view dedups via `QUALIFY ROW_NUMBER()` preferring rows with location/customer data.
4. **Daily pipeline lookback** — 2 days (`Date.now() - 172800000`) to catch same-day orders missed by the 1-day window.
5. **Backfills** — always use `created_at_min/max` (never `updated_at`) to match Shopify Admin counts. Never prefix dates with `=` in n8n.
6. **Store location** — `order.location_id` mapped to 5 real stores + warehouse/consignment locations.
7. **Channel mapping** — Point of Sale→Retail · Online Store/Shop→Ecomm · Draft Orders→Draft · 3890849→Gorgias · else Other.

## Store Location Map

| location_id | Store |
|---|---|
| 61845110897 | 2061 West 4th Ave |
| 34791915633 | 418 Davie Street, Vancouver |
| 70972768369 | 486 Front St W - The Well, Toronto |
| 69315657841 | 510 8 Ave SW - Holt Renfrew, Calgary |
| 61826072689 | 79 Yorkville, Toronto |

## Dashboards (Metabase)

1. **Leadership Snapshot** — Overview · MTD KPIs · Trends
2. **Inventory & Buying** — Overview · Aging · Condition & Location · Inventory · Products
3. **Retail** — KPIs · Trends
4. **Ecomm** — KPIs · Trends
5. **Customers** — Overview
6. **Supplier & Seller** — Overview
7. **Shipping & Operations** — Overview
8. **Marketing** — Paid Media · Email (Klaviyo)

See `Meta Base Dashboards/` for every question and its SQL.

---

## ⚠️ Security Note Before Pushing

The pipeline JSONs and Python scripts contain **hardcoded credentials** (Shopify access token, BigQuery service-account private key). Before pushing to GitHub:

1. **Make the repo PRIVATE**, or
2. Replace secrets with placeholders (`SHOPIFY_TOKEN = "YOUR_TOKEN"`) and load from environment variables / Colab secrets.

If the repo was ever public with these keys, rotate the Shopify token and the BigQuery service-account key immediately.
