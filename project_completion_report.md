# Full Project Completion Report
**Project:** Analytics & Reporting Pipeline
**Client:** Mine & Yours (Luxury Resale)
**Agency:** Buildberg
**Date:** June 19, 2026
**Prepared by:** Ahad

---


## Phase 3 — Data Pipelines & Modeling ✅

### Shopify Pipelines (n8n → BigQuery, daily 1PM)

| Pipeline | What it pulls | Status |
|---|---|---|
| shopify_orders | All orders with line items, UTM, channel, financials | ✅ Live |
| shopify_customers | All customers with tags (cognito-consignment seller identification) | ✅ Live |
| shopify_products | Products with inventory item costs (separate API call) | ✅ Live |
| shopify_product_metafields | buy.* and custom.* metafields (contract type, condition, location, seller name) | ✅ Live |
| shopify_refunds | Refund line items with order mapping | ✅ Live |

### Marketing Pipelines

| Pipeline | What it pulls | Status |
|---|---|---|
| Meta Ads | Ad-level spend, impressions, clicks, reach, purchases, ROAS via Facebook Graph API | ✅ Live |
| Google Ads | Campaign-level spend and conversions via Windsor (temporary — pending Standard access) | ✅ Live |
| Klaviyo Campaigns | Campaign metadata, send time, status | ✅ Live |
| Klaviyo Lists | List names and metadata | ✅ Live |
| Klaviyo Campaign Metrics | Opens, clicks, open rate, click rate, unsubscribes, revenue per campaign | ✅ Live |

### Backfills Completed

| Backfill | Period | Method |
|---|---|---|
| Customers (all-time + tags) | 2026-01-01 → present | Python / Colab |
| Products + inventory costs | 2026-04-01 → present | Python / Colab |
| Product metafields | 2026-03-01 → Jun 10 | Python / Colab |
| Refunds | Jun 4 → Jun 9 | n8n manual |
| Meta Ads | 2026-01-01 → present | Python / Colab |

### Reporting Views (BigQuery — final_reporting)

| View | Source Tables | Key Logic |
|---|---|---|
| fact_orders_v2 | shopify_orders | Order-level with COGS, gross profit, UTM, channel, deduped by order_id |
| fact_daily_sales_v2 | shopify_orders | Daily aggregated sales by channel, includes all statuses except cancelled |
| fact_product_sales_v2 | shopify_orders | Line-item level sales with cost and margin per product |
| fact_customers_v2 | shopify_customers | Latest snapshot per customer, new vs returning, LTV, AOV, purchase segment |
| fact_inventory_v2 | shopify_products + metafields | Current active inventory with aging, condition, location, cost excl. consignment |
| fact_refunds_v2 | shopify_refunds + orders | Clean refund records with channel mapping, filters empty rows |
| fact_marketing | meta_ads + google_ads | UNION ALL of Meta and Google with type casting |
| fact_klaviyo_campaigns | klaviyo_metrics + campaigns + messages | Campaign performance with name join |
| fact_seller | shopify_product_metafields + shopify_customers | Sellers identified via cognito-consignment-update tag, 232 seller-buyer overlaps |

### Data Quality

| Check | Result |
|---|---|
| Revenue vs Shopify Admin (30 days) | $558,232 BQ vs CA$556,500 Shopify — 0.3% diff ✅ |
| Order count vs Shopify (Jun 5–11) | 498 BQ vs 515 Shopify — 3.3% diff (created vs updated date) ✅ |
| Duplicates | Removed from all raw tables and views via QUALIFY ROW_NUMBER() |
| Dedup logic | All 9 views use QUALIFY ROW_NUMBER() — one row per entity |
| Historical coverage | 51,843 orders · $118M revenue · Feb 2024 – present |
| Consignment sellers identified | 2,159 customers tagged via cognito-consignment-update |
| Seller-buyer overlap | 232 sellers who also purchase from Mine & Yours |
| Inventory cost coverage | 20% of products have cost entered (client to improve at intake) |

---

## Phase 4 — Dashboards (Metabase) ✅

**BI Tool:** Metabase Starter — $100/month — connected to BigQuery

### Dashboards Built

---

### 1. Leadership Snapshot
**Tabs:** MTD KPIs · Trends

**MTD KPIs (12 cards):**
Net Sales MTD · Gross Profit MTD · Gross Margin % MTD · Total Inventory Retail Value · Total Inventory Cost (excl. consignment) · Sell-through Rate (30 days) · Total Orders MTD · Total Units Sold MTD · Total Inventory Cost · Return Orders MTD · Refunded Units MTD · Refunded Value MTD

**Trends (8 charts):**
Net Sales Daily Trend · Net Sales by Channel Over Time · Orders by Day · AOV by Day · Units Sold by Day · Gross Margin % by Day · Returns by Day · Refunded Value by Day

---

### 2. Inventory & Buying
**Tabs:** Overview · Aging · Condition & Location · Inventory

**Overview (5 cards):**
Units on Hand · On-Hand Retail Value · On-Hand Cost (excl. consignment) · % Consignment in Stock · Units by Location

**Aging (6 cards):**
% Aging Over 90 Days · Products by Aging Bucket · Retail Value by Aging Bucket · Dead Stock Units · Avg Days in Inventory · Text explanation of how aging is calculated

**Condition & Location (3 cards):**
Products by Condition Grade · Retail Value by Condition Grade · Condition Grade Summary Table

**Inventory (1 card):**
Full Inventory Table — all active products with cost, aging, condition, location, seller name

**Filters:** Location · Contract Type

---

### 3. Shipping & Operations
**Tabs:** Overview

**5 cards:**
Shipping Revenue · Total Orders · Orders by Channel · Shipping Revenue by Day · Returns by Channel

**Filters:** Date Range · Channel

---

### 4. Supplier & Seller
**Tabs:** Overview

**5 cards:**
Items Supplied by Contract Type · Top 20 Sellers by Units · Sellers Who Also Buy (table) · Sellers by Contract Type · Seller Activity

**Filters:** Date Range (last_buy_date) · Contract Type

---

### 5. Customers
**Tabs:** Overview

**5 cards:**
New vs Returning Customers · Purchase Segments · Repeat Customers · Average Customer LTV · Top 20 Customers by Spend

**Filters:** Date Range (customer_created_at)

---

### 6. Retail
**Tabs:** MTD KPIs · Trends

**MTD KPIs (6 cards):**
Retail Net Sales · Retail Gross Profit · Retail AOV · Retail Orders · Retail Units Sold · Retail Return Orders

**Trends (3 charts):**
Retail Sales by Day · Retail Orders by Day · Retail vs Ecomm Sales

**Filters:** Date Range

---

### 7. Ecomm
**Tabs:** MTD KPIs · Trends

**MTD KPIs (6 cards):**
Ecomm Net Sales · Ecomm Orders · Ecomm AOV · Ecomm Units Sold · Ecomm Gross Profit · Ecomm Return Orders

**Trends (3 charts):**
Ecomm Sales by Day · Ecomm Orders by Day · Sales by UTM Source

**Filters:** Date Range

---

### 8. Marketing
**Tabs:** Paid Media · Email (Klaviyo)

**Paid Media (5 cards):**
Total Marketing Spend · Spend by Channel · ROAS by Channel · Daily Spend by Channel · Conversions by Channel

**Email — Klaviyo (4 cards):**
Total Email Sends · Avg Open Rate · Avg Click Rate · Campaign Performance Table

**Filters:** Date Range

---

## Open Items (Client Action Required)

| Item | Impact | Priority |
|---|---|---|
| Upgrade Google Ads access Read Only → Standard | Will enable n8n pipeline replacing Windsor | 🔴 High |
| Enter product costs in Shopify at intake | Currently 20% coverage — affects gross margin and inventory cost | 🔴 High |
| Configure Klaviyo conversion metric | Email revenue showing $0 — conversion tracking not set up | 🟡 Medium |
| Share sales goals sheet | % to Plan KPI cannot be built without targets | 🟡 Medium |
| Fill buy.customer_id at intake | Currently 3 records only — needed for full seller↔buyer mapping | 🟡 Medium |

---

## Infrastructure Summary

| Component | Detail |
|---|---|
| Data Warehouse | Google BigQuery — mine-and-yours-analytics |
| Orchestration | n8n on Railway |
| BI Tool | Metabase Starter — metabase.mine-and-yours.com |
| Raw Layer | raw_shopify (5 tables) · raw_marketing (6 tables) |
| Reporting Layer | final_reporting (9 views) |
| Daily Refresh | 1PM PKT — all pipelines |
| Historical Coverage | Feb 2024 – present · 51,843 orders · $118M revenue |
| Sellers Identified | 2,159 consignment sellers · 232 also buyers |

