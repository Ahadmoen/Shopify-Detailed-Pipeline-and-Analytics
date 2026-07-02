# Mine & Yours — Metabase Dashboard Structure

---

## 1. Leadership Snapshot
*High-level business performance for leadership and management*

**Filters:** Date Range

| Tab | Cards | Purpose |
|---|---|---|
| **Overview** | Orders · Units Sold · Net Sales · Refunded Units · Orders by Channel · Orders by Channel and Province | High-level order and sales summary with channel and location breakdown |
| **MTD KPIs** | Net Sales · Gross Profit · Gross Margin % · AOV · Total Orders · Units Sold · Inventory Retail Value · Inventory Cost · Sell-through Rate · Return Orders · Refunded Units · Refunded Value | Current month KPIs — defaults to this month, date filter to change period |
| **Trends** | Net Sales Daily · Sales by Channel · Orders by Day · AOV by Day · Units by Day · Gross Margin % by Day · Returns by Day · Refunded Value by Day | Visual trends over selected period |

---

## 2. Inventory & Buying
*Current and historical inventory health across all locations*

**Filters:** As of Date · Location · Contract Type

| Tab | Cards | Purpose |
|---|---|---|
| **Overview** | Units on Hand · Retail Value · Cost excl. Consignment · % Consignment · Units by Location | Summary of current stock value and distribution |
| **Aging** | % Aging Over 90 Days · Products by Aging Bucket · Retail Value by Aging Bucket · Dead Stock Units · Avg Days in Inventory · How aging is calculated (text) | Identifies slow-moving and at-risk inventory |
| **Condition & Location** | Products by Condition Grade · Retail Value by Condition · Condition Summary Table | Quality mix and store distribution of current stock |
| **Inventory** | Full Inventory Table | Complete product list with cost, aging, condition, location and seller |

---

## 3. Retail
*In-store POS sales performance*

**Filters:** Date Range · Ship Province (store location proxy)

| Tab | Cards | Purpose |
|---|---|---|
| **KPIs** | Net Sales · Gross Profit · AOV · Orders · Units Sold · Return Orders | Retail performance for selected period |
| **Trends** | Sales by Day · Orders by Day · Retail vs Ecomm | Daily retail trend and channel comparison |

---

## 4. Ecomm
*Online store performance*

**Filters:** Date Range

| Tab | Cards | Purpose |
|---|---|---|
| **KPIs** | Net Sales · Orders · AOV · Units Sold · Gross Profit · Return Orders | Online performance for selected period |
| **Trends** | Sales by Day · Orders by Day · Sales by UTM Source | Daily ecomm trend and traffic source breakdown |

---

## 5. Customers
*Customer behaviour, retention and lifetime value*

**Filters:** Date Range (customer created date)

| Tab | Cards | Purpose |
|---|---|---|
| **Overview** | New vs Returning · Purchase Segments · Repeat Customers · Avg LTV · Top 20 by Spend | Customer segmentation and value analysis |

---

## 6. Supplier & Seller
*Supplier performance and seller-buyer overlap*

**Filters:** Date Range (last buy date) · Contract Type

| Tab | Cards | Purpose |
|---|---|---|
| **Overview** | Items by Contract Type · Top 20 Sellers by Units · Sellers Who Also Buy · Sellers by Contract Type | Supplier volume, contract mix and buying overlap |

---

## 7. Shipping & Operations
*Order volume, shipping revenue and returns*

**Filters:** Date Range · Channel

| Tab | Cards | Purpose |
|---|---|---|
| **Overview** | Shipping Revenue · Total Orders · Orders by Channel · Shipping Revenue by Day · Returns by Channel | Operational performance and shipping metrics |

---

## 8. Marketing
*Paid media spend and email campaign performance*

**Filters:** Date Range

| Tab | Cards | Purpose |
|---|---|---|
| **Paid Media** | Total Spend · Spend by Channel · ROAS by Channel · Daily Spend Trend · Conversions by Channel | Meta and Google Ads performance |
| **Email (Klaviyo)** | Total Sends · Avg Open Rate · Avg Click Rate · Campaign Performance Table | Email campaign engagement metrics |

