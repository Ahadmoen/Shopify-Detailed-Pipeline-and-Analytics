# Shopify Detailed Pipeline and Analytics — Full Technical Documentation

**Client:** Mine & Yours — luxury resale, 5 stores (Vancouver ×2, Toronto ×2, Calgary ×1)
**Stack:** Shopify + Meta Ads + Google Ads + Klaviyo → n8n (Railway) → Google BigQuery → Metabase

---

# 1. System Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │              DATA SOURCES                     │
                    │  Shopify Admin API (2024-01)                  │
                    │  Facebook Graph API (Meta Ads)                │
                    │  Google Ads (via Windsor / AppScript)         │
                    │  Klaviyo API                                  │
                    └──────────────┬───────────────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────────────┐
                    │  INGESTION                                    │
                    │  n8n on Railway — daily 1PM, 2-day lookback   │
                    │  Python Colab scripts — historical backfills  │
                    └──────────────┬───────────────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────────────┐
                    │  BIGQUERY  mine-and-yours-analytics           │
                    │  (us-central1)                                │
                    │  raw_shopify (5 tables)                       │
                    │  raw_marketing (6 tables)                     │
                    │  final_reporting (9 views)                    │
                    └──────────────┬───────────────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────────────┐
                    │  METABASE (Starter) — 8 dashboards            │
                    └──────────────────────────────────────────────┘
```

---

# 2. Raw Layer

## 2.1 raw_shopify

| Table | Source endpoint | Grain | Key columns added during project |
|---|---|---|---|
| shopify_orders | /orders.json | order × line item × pipeline day | `order_location_id`, `order_location_name`, `order_customer_id` |
| shopify_customers | /customers.json | customer × pipeline day | `customer_tags` (seller identification) |
| shopify_products | /products.json + /inventory_items.json | product × pipeline day | `product_variant_inventory_item_cost` (second API call) |
| shopify_product_metafields | /products/{id}/metafields.json | product × namespace × key | buy.* and custom.* namespaces |
| shopify_refunds | /orders refunds | refund line | `line_item__refunds_subtotal` etc. |

**Important schema facts**
- All money/quantity columns are **BIGNUMERIC** — Python inserts must convert with `Decimal(str(round(x,4)))` and pass an explicit schema.
- `order_created_at` is stored as **STRING** — cast with `TIMESTAMP()` before use.
- `date` column = the day the pipeline inserted the row (NOT the order date). Views never group on it.
- Orders table is **partitioned by `date` (day)** — `CREATE OR REPLACE TABLE ... AS SELECT` without a partition spec fails; use CREATE clean → TRUNCATE → INSERT → DROP.

## 2.2 raw_marketing

| Table | Source |
|---|---|
| meta_ads | Facebook Graph API — account act_2626840940790152 currently returns **no data**, client to verify |
| google_ads | Windsor / Google Ads AppScript (temporary until Standard API access granted) |
| klaviyo_campaigns / klaviyo_lists / klaviyo_campaign_messages / klaviyo_campaign_metrics | Klaviyo API — pipeline pulls last 30 days per run (self-healing) |

---

# 3. Pipelines

## 3.1 Daily n8n pipelines (1PM)

Every Shopify workflow follows the same skeleton:

```
Schedule (1PM) → Get First Page (HTTP) → Initialize Pagination →
Has More Pages? ──yes──► Fetch Next Page → Merge Pages ─┐
        │ no                                            │
        ▼◄──────────────────────────────────────────────┘
    Transform (Code) → Insert → BigQuery
```

**Daily date filter** (orders):
```javascript
updated_at_min = new Date(Date.now() - 172800000)  // 2-day lookback
updated_at_max = new Date()                        // today
```
2 days instead of 1 because orders created before the 1PM run but never updated again were slipping through the 1-day window. Views dedupe so the overlap is safe.

**Backfill branch** (Manual Trigger in same workflow):
- Uses **`created_at_min` / `created_at_max`** — NOT `updated_at`. `updated_at` over-fetches: a May backfill returned 2,779 orders when Shopify Admin showed 2,447 because it swept up older orders merely touched in May. `created_at` returned 2,478 ✅.
- **Never prefix date values with `=`** — Shopify silently ignores the filter (recurring bug that was fixed twice).

**Transform node — key logic** (orders):
```javascript
var appMap = {web:'Online Store', pos:'Point of Sale', mobile:'Shop',
              shopify_draft_order:'Draft Orders', iphone:'Shop', android:'Shop'};

var locationMap = {
  '61845110897': '2061 West 4th Ave',
  '34791915633': '418 Davie Street, Vancouver',
  '70972768369': '486 Front St W - The Well, Toronto',
  '69315657841': '510 8 Ave SW - Holt Renfrew, Calgary',
  '61826072689': '79 Yorkville, Toronto',
  '42702532':    '1025 Howe Street, Vancouver',
  '61808017521': 'Consignment - Real Real',
  '61822697585': "Courtney's Closet",
  '191632':      'Storage Locker',
  '61841834097': 'West 4th - Back of House (Archived)'
};

order_location_id   = o.location_id?.toString() || null
order_location_name = locationMap[order_location_id] || 'Unknown Location'
order_customer_id   = o.customer ? o.customer.id.toString() : null
```
One row per line item; orders with no line items get one row with null line_item fields.

**n8n "malicious string" error fix:** newer n8n versions block dynamic string-concatenated URLs (`url + $json.batches[$json.batchIdx]`). Fix: static URL + pass ids as a **query parameter**.

## 3.2 Python backfill scripts (Colab)

Preferred over n8n for large ranges (35K orders in minutes vs hours). Pattern per script:

1. Count existing rows in the target date range (logged).
2. Attempt `DELETE` — **frequently blocked by the streaming buffer** (rows inserted by n8n streaming inserts are locked from DELETE/UPDATE for ~30-90 min). On failure: skip delete, append, and dedupe afterwards.
3. Fetch via `created_at_min/max` with Link-header pagination (250/page).
4. Transform — identical field mapping to n8n including locationMap and customer_id. `get_week()` must strip tzinfo (`dt.replace(tzinfo=None)`) or datetime subtraction throws.
5. Insert with explicit **BIGNUMERIC schema** + `df["date"] = pd.to_datetime(df["date"]).dt.date`.
6. Verify: total rows, unique orders, has_location, has_customer_id, date range, deleted-vs-inserted summary.

## 3.3 The dedupe pattern (post-backfill)

Raw tables tolerate duplicates by design; clean-up when they accumulate:

```sql
CREATE OR REPLACE TABLE raw_shopify.shopify_orders_clean AS
SELECT * FROM raw_shopify.shopify_orders
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY order_id, date, line_item__id
  ORDER BY
    CASE WHEN order_location_name IS NOT NULL THEN 0 ELSE 1 END,  -- prefer rows with location
    CASE WHEN order_customer_id  IS NOT NULL THEN 0 ELSE 1 END,   -- then rows with customer id
    date DESC
) = 1;
-- verify count matches expectation, then:
TRUNCATE TABLE raw_shopify.shopify_orders;
INSERT INTO raw_shopify.shopify_orders SELECT * FROM raw_shopify.shopify_orders_clean;
DROP TABLE raw_shopify.shopify_orders_clean;
```

Status progression is preserved because `date` is inside the partition key — an order paid on day 1 and refunded on day 5 keeps both rows. Only same-day duplicates (pipeline reruns) collapse.

---

# 4. Reporting Views — final_reporting

## 4.1 Shared conventions (every view)

**Timezone** — store operates GMT-8 (Vancouver). Shopify stores UTC, so orders after ~4-5PM local landed on the next date and nothing reconciled with Shopify Admin. Fix everywhere:
```sql
DATE(DATETIME(TIMESTAMP(order_created_at), 'America/Vancouver')) AS order_date
```
(`America/Vancouver` handles PST/PDT automatically.) After this fix Jun 15 = 47 orders (Shopify 45), May = 2,438 (Shopify 2,447 → 0.4%).

**Channel mapping**
```sql
CASE
  WHEN order_app_name = 'Point of Sale'           THEN 'Retail'
  WHEN order_app_name IN ('Online Store','Shop')  THEN 'Ecomm'
  WHEN order_app_name = 'Draft Orders'            THEN 'Draft'
  WHEN order_app_name = '3890849'                 THEN 'Gorgias'   -- Gorgias chat app id
  ELSE 'Other'                                                     -- e.g. '2329312', eBay Integration - DPL
END AS channel
```

**Dedup inside every view** — `QUALIFY ROW_NUMBER() OVER (PARTITION BY <entity> ORDER BY location-first, date DESC) = 1`, so dashboards stay correct even if raw contains duplicates.

**Test/cancelled filter** — `LOWER(COALESCE(order_test,'false'))='false' AND LOWER(order_financial_status)!='cancelled'`.

## 4.2 View-by-view

### fact_orders_v2 (order grain)
- `latest_costs` CTE joins **product cost from shopify_products** — because the Shopify Orders API does **not** return `variant_unit_cost` at all (verified empirically: field absent from every line item; see check_order_cost_field.py). COGS = qty × `product_variant_inventory_item_cost`.
- COGS coverage ≈ 20% of products (client enters costs at intake) → margin currently reads ~93% and will normalize as coverage grows.
- Outputs: order_date, channel, sales_channel, financial_status, ship_country/province, **store_location_id, store_location, order_customer_id**, net_sales, subtotal/gross revenue, discounts, shipping, tax, UTM (last-visit), total_units, cogs, gross_profit, gross_margin_pct.

### fact_daily_sales_v2 (day × channel × geo × store)
Aggregates net_sales, discounts, shipping, gross_revenue, units, AOV. `net_sales` = `subtotal_price` (after discounts, **before returns**) — see §6 reconciliation.

### fact_product_sales_v2 (product × day × channel × store)
Line-item sales with the same cost join, margin per product, excludes gift cards / paper bags. This view powers the **Inventory “Products” tab** — the bridge answering “where was inventory sold” since unsold inventory has no channel.

### fact_refunds_v2 (refund line)
Dedupes refund rows on (order_id, refund url, subtotal, quantity), extracts `refund_id` via `REGEXP_EXTRACT(order_refunds, r'/(\d+)$')`, joins channel + store_location + geography from the parent order. Refund money column is `line_item__refunds_subtotal` (there is no `refund_subtotal`).

### fact_customers_v2 (customer grain)
Latest snapshot per customer + segments, **plus** join to raw orders via the new `order_customer_id`:
```sql
ARRAY_AGG(order_location_name IGNORE NULLS ORDER BY date DESC LIMIT 1)[SAFE_OFFSET(0)] AS preferred_store
ARRAY_AGG(<channel case>      IGNORE NULLS ORDER BY date DESC LIMIT 1)[SAFE_OFFSET(0)] AS preferred_channel
```
Verified: Yorkville 1,227 · Davie 724 · West 4th 701 · Calgary 207 · The Well 124; Retail 2,806 · Ecomm 1,044 · Draft 165 · Gorgias 42.
(Customer city/country also available but that is home address, not store.)

### fact_inventory_v2 (product snapshot)
- `snapshot_date` = products pipeline `date` → Metabase single-date **“As of Date”** filter shows inventory as of any past day (a date *range* resolves to the latest state inside the range — it is a point-in-time snapshot, not a daily series; a daily-trend view was prototyped and dropped because the daily pipeline only captures *updated* products, so per-day totals were partial).
- Aging computed **buy_date → snapshot_date** (not CURRENT_DATE) so historical snapshots age correctly. Buckets: 0-30 / 31-60 / 61-90 / 91-180 / 180+.
- **store_location** comes from the `custom.location` metafield which is stored as a JSON array (`["79 Yorkville, Toronto"]`) — cleaned with:
```sql
REGEXP_EXTRACT(<location metafield>, r'"([^"]+)"') AS store_location
```
- `cost_excl_consignment` — consignment items carry no owned cost.
- Channel: **not applicable** (unsold stock has no sales channel — by design).

### fact_seller — seller/buyer identity resolution (asked-about detail)
**How sellers are identified:**
1. **Seller side** — products carry `buy.*` metafields written at intake: `seller_name`, `contract_type` (consignment / buyout / store_credit), `date`, `msrp`, `condition_notes`. Grouping these per seller gives items supplied, contract mix, first/last buy dates.
2. **Store where items were received** — `custom.location` metafield per product (JSON-array cleaned as above).
3. **Channel of their sold items** — join to `fact_product_sales_v2` on product_id (latest sale). Empty channel = item still unsold.
4. **Buyer side** — customers who submitted the consignment form carry the Shopify tag **`cognito-consignment-update`** (2,159 customers). 
5. **Seller ↔ buyer match** — name join:
```sql
LOWER(TRIM(seller_name)) = LOWER(CONCAT(TRIM(customer_first_name),' ',TRIM(customer_last_name)))
```
→ **232 sellers also buy** from Mine & Yours, with their buyer_orders_count / buyer_total_spent / buyer_aov exposed. Name matching is best-effort; `buy.customer_id` metafield exists but is populated on only ~3 records — client action item to fill at intake for an exact key.

### fact_marketing_v2
UNION ALL of meta_ads + google_ads with type casting into one schema (source, campaign/adgroup/ad, spend, impressions, clicks, reach, conversions, conversion_value, roas).

### fact_klaviyo_campaigns_v2
Campaign metrics joined to campaign names; revenue currently $0 — Klaviyo conversion metric not configured (client action).

---

# 5. Store Location — full pipeline story

1. `order_shipping_address_province` was tried first — but that is the **customer’s address**, not the store; POS orders often have it blank, and Zoey confirmed “by location = by store, not city”.
2. Verified via API (check_location_field.py): every POS order carries **`location_id`**; the Locations endpoint returned all 10 locations (5 real stores + Howe St legacy + Real Real consignment + Courtney's Closet + Storage Locker + archived back-of-house).
3. Added `order_location_id` + mapped `order_location_name` to both n8n Transform nodes and the Python backfill; `ALTER TABLE ... ADD COLUMN` on raw.
4. Backfilled 2025-01-01 → 2026-06-28 (35,332 orders fetched) then deduped preferring located rows → Retail location coverage 17% → **65%** (remaining nulls are orders predating location tracking — accepted).
5. All order-based views expose `store_location`; inventory/seller use the metafield location (different source, same 5 stores).
6. Consignment/warehouse “locations” stay in the map for completeness but are excluded from dashboard filter dropdowns (only the 5 customer-facing stores).

---

# 6. Reconciliation vs Shopify Admin (why numbers differ, and by how much)

| Cause | Explanation | Status |
|---|---|---|
| Timezone | UTC vs GMT-8 shifted evening orders to next day | **Fixed** — America/Vancouver everywhere |
| Net sales definition | Our `net_sales` = subtotal after discounts, **before returns**; Shopify Net Sales subtracts returns. May check: ours 2,885,394 − returns 296,702 = 2,588,692 vs Shopify 2,585,902 (Δ $2.8K ≈ 0.1%) | Accepted definitional difference |
| Gross revenue | `order_total_price` includes shipping + tax; Shopify “gross sales” excludes them | Known — use net_sales for comparisons |
| Attribution reports | Shopify “last non-direct click” reports **redistribute** revenue — never reconcile against them | Documented |
| Raw `date` vs order date | Raw `date` = pipeline insert day — raw counts never match views by design | Documented |
| Duplicates | Same-day pipeline reruns (worst case one order ×143) | Views dedupe; raw cleaned via §3.3 |
| Same-day pipeline gap | 1PM run with 1-day lookback missed same-day orders | **Fixed** — 2-day lookback |
| COGS coverage | 20% of products have cost → margin overstated | Client action: enter costs at intake |

---

# 7. Metabase — 8 Dashboards

Structure in repo: `Meta Base Dashboards/<Dashboard>/<Tab>/queries_and_purpose.md` (every question + SQL).

| # | Dashboard | Tabs | Filters |
|---|---|---|---|
| 1 | Leadership Snapshot | Overview · MTD KPIs · Trends | Date · Store Location · Channel |
| 2 | Inventory & Buying | Overview · Aging · Condition & Location · Inventory · **Products** | As-of Date · Store Location · Contract Type |
| 3 | Retail | KPIs · Trends | Date · Store Location |
| 4 | Ecomm | KPIs · Trends | Date |
| 5 | Customers | Overview | Date · Store Location · Channel |
| 6 | Supplier & Seller | Overview | Date (last_buy) · Contract · Store · Channel |
| 7 | Shipping & Operations | Overview | Date · Channel · Store |
| 8 | Marketing | Paid Media · Email (Klaviyo) | Date |

**Date comparison** — Metabase Starter has no native "Compare to another period"; Number cards use the **Trend** chart type which shows value + % change vs previous period. Implemented on Leadership Overview; client can replicate on any card (video walkthrough recorded).

**Filter self-service** — filters map to `store_location` / `channel` columns now present in every applicable view; client adds via filter icon → Text or Category → map column.

---

# 8. Open Items (client actions)

| Item | Impact |
|---|---|
| Google Ads Standard API access | Replaces temporary Windsor feed |
| Enter product costs in Shopify at intake | COGS coverage 20% → accurate margins |
| Configure Klaviyo conversion metric | Email revenue currently $0 |
| Sales goals sheet | % to Plan KPI blocked |
| Confirm Meta Ads running + recheck credentials | act_2626840940790152 returns no data |
| Fill buy.customer_id at intake | Exact seller↔buyer key (currently name-match) |

---

# 9. Security

Pipeline JSONs and scripts contain the Shopify access token and BigQuery service-account private key. Keep the repository **private**, or sanitize to environment variables before any public push. If ever exposed publicly, rotate both credentials immediately.
