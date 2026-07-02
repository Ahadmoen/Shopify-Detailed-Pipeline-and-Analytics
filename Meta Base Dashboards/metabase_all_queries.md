# Mine & Yours — Metabase Dashboard Queries
**All queries use BigQuery project: `mine-and-yours-analytics`**
**For each question: + New → Question → Native Query → BigQuery**

---

## 1. LEADERSHIP SNAPSHOT

### Tab: MTD Numbers

---
**Name:** `Net Sales MTD`
**Description:** `Total net sales for the current month to date across all channels`
```sql
SELECT ROUND(SUM(net_sales), 2) AS net_sales_mtd
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Gross Margin % MTD`
**Description:** `Gross profit as a percentage of net sales for current month`
```sql
SELECT ROUND(SUM(gross_profit) / NULLIF(SUM(net_sales), 0) * 100, 1) AS gross_margin_pct
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Suffix: `%`

---
**Name:** `AOV MTD`
**Description:** `Average order value (net sales / orders) for current month`
```sql
SELECT ROUND(SUM(net_sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS aov
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Total Inventory Retail Value`
**Description:** `Total retail value of all active products currently in stock`
```sql
SELECT ROUND(SUM(retail_value), 2) AS total_retail_value
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Total Inventory Cost (excl. consignment)`
**Description:** `Total cost value of owned inventory excluding consignment items`
```sql
SELECT ROUND(SUM(cost_excl_consignment), 2) AS total_cost_excl_consignment
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Sell-through Rate (30 days)`
**Description:** `Units sold in last 30 days as a % of total available units (sold + on hand)`
```sql
SELECT ROUND(
  SUM(units_sold) / NULLIF(SUM(units_sold) + SUM(units_on_hand), 0) * 100, 1
) AS sell_through_pct
FROM (
  SELECT SUM(units_sold) AS units_sold, 0 AS units_on_hand
  FROM `mine-and-yours-analytics.final_reporting.fact_product_sales_v2`
  WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  UNION ALL
  SELECT 0, SUM(units_on_hand)
  FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
  WHERE units_on_hand > 0
)
```
Visualization: **Number** | Suffix: `%`

---
**Name:** `Inventory Turnover (Annual)`
**Description:** `How many times inventory is sold and replaced in a year (COGS / avg inventory cost)`
```sql
SELECT ROUND(
  SUM(o.cogs) / NULLIF(AVG(i.cost_excl_consignment), 0), 2
) AS inventory_turnover
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2` o
CROSS JOIN (
  SELECT SUM(cost_excl_consignment) AS cost_excl_consignment
  FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
  WHERE units_on_hand > 0
) i
WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
```
Visualization: **Number** | Suffix: `x`

---
**Name:** `Days Inventory Outstanding (DIO)`
**Description:** `Average number of days inventory sits before being sold`
```sql
SELECT ROUND(365 / NULLIF(
  SUM(o.cogs) / NULLIF(AVG(i.cost_excl_consignment), 0), 0
), 0) AS dio_days
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2` o
CROSS JOIN (
  SELECT SUM(cost_excl_consignment) AS cost_excl_consignment
  FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
  WHERE units_on_hand > 0
) i
WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
```
Visualization: **Number** | Suffix: ` days`

---
**Name:** `Active Customers (12 months)`
**Description:** `Unique customers who have placed at least one order in the last 12 months`
```sql
SELECT COUNT(DISTINCT customer_id) AS active_customers
FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
WHERE customer_orders_count > 0
  AND DATE(customer_updated_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
```
Visualization: **Number**

---
**Name:** `Repeat Purchase Rate`
**Description:** `Percentage of customers who have placed more than one order`
```sql
SELECT ROUND(
  COUNTIF(customer_type = 'Returning') / COUNT(*) * 100, 1
) AS repeat_rate_pct
FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
WHERE customer_orders_count > 0
```
Visualization: **Number** | Suffix: `%`

---
**Name:** `Customer LTV`
**Description:** `Average lifetime value (total spent) per customer`
```sql
SELECT ROUND(AVG(total_spent), 2) AS avg_ltv
FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
WHERE customer_orders_count > 0
```
Visualization: **Number** | Prefix: `$`

---

### Tab: Trends

---
**Name:** `Net Sales Daily Trend`
**Description:** `Daily net sales for the last 30 days across all channels`
```sql
SELECT order_date, ROUND(SUM(net_sales), 2) AS net_sales
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY order_date ORDER BY order_date
```
Visualization: **Line** | X: `order_date` | Y: `net_sales`

---
**Name:** `Net Sales by Channel MTD`
**Description:** `Net sales split by Retail, Ecomm and Draft channels for current month`
```sql
SELECT channel, ROUND(SUM(net_sales), 2) AS net_sales
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY channel ORDER BY net_sales DESC
```
Visualization: **Bar** | X: `channel` | Y: `net_sales`

---

## 2. RETAIL SCORECARD

### Tab: MTD Numbers

---
**Name:** `Retail Net Sales MTD`
**Description:** `Net sales from POS/in-store retail channel for current month`
```sql
SELECT ROUND(SUM(net_sales), 2) AS retail_net_sales
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE channel = 'Retail'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Retail LY Net Sales`
**Description:** `Retail net sales for the same month last year (year-over-year comparison)`
```sql
SELECT ROUND(SUM(net_sales), 2) AS retail_net_sales_ly
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE channel = 'Retail'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Retail COGS MTD`
**Description:** `Cost of goods sold for retail channel in current month`
```sql
SELECT ROUND(SUM(cogs), 2) AS retail_cogs
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE channel = 'Retail'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Retail Gross Profit MTD`
**Description:** `Gross profit (net sales minus COGS) for retail channel in current month`
```sql
SELECT ROUND(SUM(gross_profit), 2) AS retail_gross_profit
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE channel = 'Retail'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Retail AOV MTD`
**Description:** `Average order value for retail channel in current month`
```sql
SELECT ROUND(SUM(net_sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS retail_aov
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE channel = 'Retail'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Retail AOV LY`
**Description:** `Average order value for retail channel in same month last year`
```sql
SELECT ROUND(SUM(net_sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS retail_aov_ly
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE channel = 'Retail'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Retail UPT MTD`
**Description:** `Units per transaction for retail channel in current month`
```sql
SELECT ROUND(SUM(total_units) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS upt
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE channel = 'Retail'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number**

---
**Name:** `Retail Units Sold MTD`
**Description:** `Total units sold through retail channel in current month`
```sql
SELECT SUM(units_sold) AS units_sold
FROM `mine-and-yours-analytics.final_reporting.fact_product_sales_v2`
WHERE channel = 'Retail'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number**

---
**Name:** `Retail Returns MTD`
**Description:** `Number of return orders and refund value for retail channel in current month`
```sql
SELECT
  COUNT(DISTINCT order_id) AS return_orders,
  ROUND(SUM(refund_subtotal), 2) AS refund_value
FROM `mine-and-yours-analytics.final_reporting.fact_refunds_v2`
WHERE channel = 'Retail'
  AND DATE_TRUNC(refund_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Table**

---

### Tab: Trends

---
**Name:** `Retail Daily Sales (30 days)`
**Description:** `Daily retail net sales trend for the last 30 days`
```sql
SELECT order_date, ROUND(SUM(net_sales), 2) AS net_sales
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE channel = 'Retail'
  AND order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY order_date ORDER BY order_date
```
Visualization: **Line**

---
**Name:** `Retail MTD vs LY`
**Description:** `Daily cumulative retail sales this year vs same month last year`
```sql
SELECT
  EXTRACT(DAY FROM order_date) AS day_of_month,
  SUM(CASE WHEN EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE()) THEN net_sales ELSE 0 END) AS this_year,
  SUM(CASE WHEN EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE()) - 1 THEN net_sales ELSE 0 END) AS last_year
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE channel = 'Retail'
  AND EXTRACT(MONTH FROM order_date) = EXTRACT(MONTH FROM CURRENT_DATE())
GROUP BY 1 ORDER BY 1
```
Visualization: **Combo** (bars + line)

---

## 3. ECOMM SCORECARD

### Tab: MTD Numbers

---
**Name:** `Ecomm Net Sales MTD`
**Description:** `Net sales from online store for current month`
```sql
SELECT ROUND(SUM(net_sales), 2) AS ecomm_net_sales
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE channel = 'Ecomm'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Ecomm Total Orders MTD`
**Description:** `Total number of online orders placed in current month`
```sql
SELECT COUNT(DISTINCT order_id) AS total_orders
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE channel = 'Ecomm'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number**

---
**Name:** `Ecomm AOV MTD`
**Description:** `Average order value for online channel in current month`
```sql
SELECT ROUND(SUM(net_sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS ecomm_aov
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE channel = 'Ecomm'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Ecomm UPT MTD`
**Description:** `Average units per online transaction in current month`
```sql
SELECT ROUND(SUM(total_units) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS upt
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE channel = 'Ecomm'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number**

---
**Name:** `Ecomm Return Rate MTD`
**Description:** `Percentage of ecomm orders that had a refund in current month`
```sql
SELECT ROUND(
  COUNT(DISTINCT r.order_id) / NULLIF(COUNT(DISTINCT o.order_id), 0) * 100, 1
) AS return_rate_pct
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2` o
LEFT JOIN `mine-and-yours-analytics.final_reporting.fact_refunds_v2` r
  ON o.order_id = r.order_id
WHERE o.channel = 'Ecomm'
  AND DATE_TRUNC(o.order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Suffix: `%`

---
**Name:** `Ecomm Shipping % of Sales MTD`
**Description:** `Shipping revenue as a percentage of total ecomm net sales`
```sql
SELECT ROUND(
  SUM(shipping_revenue) / NULLIF(SUM(net_sales), 0) * 100, 1
) AS shipping_pct
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE channel = 'Ecomm'
  AND DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Suffix: `%`

---
**Name:** `Ecomm Sales by UTM Source`
**Description:** `Net sales and orders broken down by marketing source (last 30 days)`
```sql
SELECT
  COALESCE(utm_source, 'Direct') AS source,
  ROUND(SUM(net_sales), 2) AS net_sales,
  COUNT(DISTINCT order_id) AS orders
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE channel = 'Ecomm'
  AND order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY 1 ORDER BY net_sales DESC
```
Visualization: **Bar**

---

## 4. CUSTOMERS SCORECARD

### Tab: Overview

---
**Name:** `New vs Returning Customers`
**Description:** `Split of customers by new vs returning based on order history`
```sql
SELECT
  customer_type,
  COUNT(*) AS total_customers,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER() * 100, 1) AS pct
FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
WHERE customer_orders_count > 0
GROUP BY customer_type
```
Visualization: **Pie**

---
**Name:** `Purchase Segments`
**Description:** `Customers grouped by No Orders, One-time, and Repeat purchasers`
```sql
SELECT
  purchase_segment,
  COUNT(*) AS customers,
  ROUND(AVG(total_spent), 2) AS avg_spent
FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
WHERE customer_orders_count > 0
GROUP BY purchase_segment ORDER BY customers DESC
```
Visualization: **Bar**

---
**Name:** `Repeat Purchase Rate`
**Description:** `Percentage of customers who have purchased more than once`
```sql
SELECT ROUND(
  COUNTIF(customer_type = 'Returning') / COUNT(*) * 100, 1
) AS repeat_rate_pct
FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
WHERE customer_orders_count > 0
```
Visualization: **Number** | Suffix: `%`

---
**Name:** `Average Customer LTV`
**Description:** `Average total lifetime spend per customer`
```sql
SELECT ROUND(AVG(total_spent), 2) AS avg_ltv
FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
WHERE customer_orders_count > 0
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `AOV by Customer Type`
**Description:** `Average order value comparing new vs returning customers`
```sql
SELECT customer_type, ROUND(AVG(aov), 2) AS avg_aov
FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
WHERE customer_orders_count > 0
GROUP BY customer_type
```
Visualization: **Bar**

---
**Name:** `Top 20 Customers by Spend`
**Description:** `Highest spending customers with order count and AOV`
```sql
SELECT
  CONCAT(first_name, ' ', last_name) AS customer_name,
  city, country, orders_count,
  ROUND(total_spent, 2) AS total_spent,
  ROUND(aov, 2) AS aov
FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
WHERE customer_orders_count > 0
ORDER BY total_spent DESC LIMIT 20
```
Visualization: **Table**

---
**Name:** `Customers by Country`
**Description:** `Customer count and total spend broken down by country`
```sql
SELECT country, COUNT(*) AS customers, ROUND(SUM(total_spent), 2) AS total_spent
FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
WHERE customer_orders_count > 0 AND country IS NOT NULL AND country != ''
GROUP BY country ORDER BY customers DESC LIMIT 15
```
Visualization: **Bar**

---

## 5. INVENTORY & BUYING SCORECARD

### Tab: Overview Numbers

---
**Name:** `Units on Hand`
**Description:** `Total active units currently in stock across all locations`
```sql
SELECT SUM(units_on_hand) AS units_on_hand
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0
```
Visualization: **Number**

---
**Name:** `On-Hand Retail Value`
**Description:** `Total retail value of all active inventory at current pricing`
```sql
SELECT ROUND(SUM(retail_value), 2) AS retail_value
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `On-Hand Cost (excl. consignment)`
**Description:** `Total cost of owned inventory excluding consignment items`
```sql
SELECT ROUND(SUM(cost_excl_consignment), 2) AS cost_excl_consignment
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `% Consignment in Stock`
**Description:** `Percentage of current inventory that is on consignment`
```sql
SELECT ROUND(
  COUNTIF(is_consignment = TRUE) / COUNT(*) * 100, 1
) AS consignment_pct
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0
```
Visualization: **Number** | Suffix: `%`

---

### Tab: Aging

---
**Name:** `Inventory Aging Breakdown`
**Description:** `Products and units grouped by how long they have been in stock`
```sql
SELECT
  aging_bucket,
  COUNT(*) AS products,
  SUM(units_on_hand) AS units,
  ROUND(SUM(retail_value), 2) AS retail_value,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER() * 100, 1) AS pct_products
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0 AND aging_bucket IS NOT NULL
GROUP BY aging_bucket
ORDER BY CASE aging_bucket
  WHEN '0-30 days' THEN 1
  WHEN '31-60 days' THEN 2
  WHEN '61-90 days' THEN 3
  WHEN '91-180 days' THEN 4 ELSE 5 END
```
Visualization: **Bar**

---
**Name:** `% Aging Over 90 Days`
**Description:** `Percentage of inventory that has been in stock more than 90 days`
```sql
SELECT ROUND(
  COUNTIF(aging_bucket IN ('91-180 days', '180+ days')) / COUNT(*) * 100, 1
) AS aging_over_90_pct
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0 AND aging_bucket IS NOT NULL
```
Visualization: **Number** | Suffix: `%`

---

### Tab: Condition & Location

---
**Name:** `Condition Grade Distribution`
**Description:** `Inventory breakdown by item condition grade`
```sql
SELECT
  COALESCE(condition_grade, 'Unknown') AS condition_grade,
  COUNT(*) AS products, SUM(units_on_hand) AS units
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0
GROUP BY condition_grade ORDER BY products DESC
```
Visualization: **Pie**

---
**Name:** `Inventory by Location`
**Description:** `Units and retail value of inventory split by store location`
```sql
SELECT
  COALESCE(location, 'Unknown') AS location,
  COUNT(*) AS products,
  SUM(units_on_hand) AS units,
  ROUND(SUM(retail_value), 2) AS retail_value
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0
GROUP BY location ORDER BY units DESC
```
Visualization: **Bar**

---
**Name:** `Contract Type Distribution`
**Description:** `Inventory breakdown by acquisition type (buyout, consignment, store credit)`
```sql
SELECT
  COALESCE(contract_type, 'Unknown') AS contract_type,
  COUNT(*) AS products,
  SUM(units_on_hand) AS units,
  ROUND(SUM(retail_value), 2) AS retail_value
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0
GROUP BY contract_type ORDER BY products DESC
```
Visualization: **Bar**

---
**Name:** `Top Vendors by Inventory Value`
**Description:** `Brands with the highest retail value currently in stock`
```sql
SELECT
  product_vendor,
  COUNT(*) AS products,
  SUM(units_on_hand) AS units,
  ROUND(SUM(retail_value), 2) AS retail_value
FROM `mine-and-yours-analytics.final_reporting.fact_inventory_v2`
WHERE units_on_hand > 0 AND product_vendor IS NOT NULL AND product_vendor != ''
GROUP BY product_vendor ORDER BY retail_value DESC LIMIT 20
```
Visualization: **Table**

---

## 6. SUPPLIER / SELLER SCORECARD

### Tab: Overview

---
**Name:** `Total Unique Sellers`
**Description:** `Total number of unique suppliers who have sold items to Mine & Yours`
```sql
SELECT COUNT(DISTINCT seller_name) AS total_sellers
FROM `mine-and-yours-analytics.final_reporting.fact_seller`
```
Visualization: **Number**

---
**Name:** `Sellers Also Buyers`
**Description:** `Number and percentage of sellers who have also purchased from Mine & Yours`
```sql
SELECT
  COUNT(DISTINCT CASE WHEN is_also_buyer THEN seller_name END) AS seller_buyers,
  COUNT(DISTINCT seller_name) AS total_sellers,
  ROUND(COUNT(DISTINCT CASE WHEN is_also_buyer THEN seller_name END) / COUNT(DISTINCT seller_name) * 100, 1) AS pct
FROM `mine-and-yours-analytics.final_reporting.fact_seller`
```
Visualization: **Table**

---
**Name:** `Top 20 Sellers by Units Supplied`
**Description:** `Highest volume suppliers ranked by total items supplied to Mine & Yours`
```sql
SELECT
  seller_name, contract_type,
  SUM(total_items_supplied) AS units_supplied,
  MIN(first_buy_date) AS first_supply_date,
  MAX(last_buy_date) AS last_supply_date,
  is_also_buyer,
  ROUND(buyer_total_spent, 2) AS also_spent_as_buyer
FROM `mine-and-yours-analytics.final_reporting.fact_seller`
GROUP BY seller_name, contract_type, is_also_buyer, buyer_total_spent
ORDER BY units_supplied DESC LIMIT 20
```
Visualization: **Table**

---
**Name:** `Items by Contract Type`
**Description:** `Total items supplied broken down by acquisition contract type`
```sql
SELECT
  contract_type,
  COUNT(DISTINCT seller_name) AS sellers,
  SUM(total_items_supplied) AS items
FROM `mine-and-yours-analytics.final_reporting.fact_seller`
GROUP BY contract_type ORDER BY items DESC
```
Visualization: **Bar**

---
**Name:** `Seller-Buyer Balance (Top 20)`
**Description:** `Sellers who also buy from Mine & Yours — comparing items supplied vs purchase spend`
```sql
SELECT
  seller_name,
  SUM(total_items_supplied) AS items_sold_to_us,
  ROUND(buyer_total_spent, 2) AS spent_buying_from_us,
  buyer_orders_count AS purchase_orders
FROM `mine-and-yours-analytics.final_reporting.fact_seller`
WHERE is_also_buyer = TRUE
GROUP BY seller_name, buyer_total_spent, buyer_orders_count
ORDER BY items_sold_to_us DESC LIMIT 20
```
Visualization: **Table**

---

## 7. MARKETING SCORECARD

### Tab: Paid Media

---
**Name:** `Total Marketing Spend MTD`
**Description:** `Combined spend across Meta Ads and Google Ads for current month`
```sql
SELECT ROUND(SUM(spend), 2) AS total_spend
FROM `mine-and-yours-analytics.final_reporting.fact_marketing`
WHERE DATE_TRUNC(date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `Spend by Channel MTD`
**Description:** `Marketing spend split between Meta and Google for current month`
```sql
SELECT source, ROUND(SUM(spend), 2) AS spend
FROM `mine-and-yours-analytics.final_reporting.fact_marketing`
WHERE DATE_TRUNC(date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY source ORDER BY spend DESC
```
Visualization: **Pie**

---
**Name:** `ROAS by Channel MTD`
**Description:** `Return on ad spend (conversion value / spend) by channel for current month`
```sql
SELECT
  source,
  ROUND(SUM(conversion_value) / NULLIF(SUM(spend), 0), 2) AS roas,
  ROUND(SUM(spend), 2) AS spend,
  ROUND(SUM(conversion_value), 2) AS conversion_value
FROM `mine-and-yours-analytics.final_reporting.fact_marketing`
WHERE DATE_TRUNC(date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY source
```
Visualization: **Table**

---
**Name:** `CAC (last 30 days)`
**Description:** `Customer acquisition cost: total ad spend divided by new customers acquired`
```sql
SELECT ROUND(
  SUM(m.spend) / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2
) AS cac
FROM `mine-and-yours-analytics.final_reporting.fact_marketing` m
CROSS JOIN (
  SELECT customer_id FROM `mine-and-yours-analytics.final_reporting.fact_customers_v2`
  WHERE customer_type = 'New'
    AND DATE(customer_created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
) c
WHERE m.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
```
Visualization: **Number** | Prefix: `$`

---
**Name:** `MER (Marketing Efficiency Ratio)`
**Description:** `Total net sales divided by total marketing spend for current month`
```sql
SELECT ROUND(
  SUM(s.net_sales) / NULLIF(SUM(m.spend), 0), 2
) AS mer
FROM (
  SELECT SUM(net_sales) AS net_sales
  FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
  WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
) s
CROSS JOIN (
  SELECT SUM(spend) AS spend
  FROM `mine-and-yours-analytics.final_reporting.fact_marketing`
  WHERE DATE_TRUNC(date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
) m
```
Visualization: **Number** | Suffix: `x`

---
**Name:** `Daily Spend by Channel (30 days)`
**Description:** `Daily marketing spend trend split by Meta and Google over last 30 days`
```sql
SELECT date, source, ROUND(SUM(spend), 2) AS spend
FROM `mine-and-yours-analytics.final_reporting.fact_marketing`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY date, source ORDER BY date
```
Visualization: **Line**

---

### Tab: Email (Klaviyo)

---
**Name:** `Email Campaigns Performance`
**Description:** `All email campaigns with sends, open rate, click rate and revenue`
```sql
SELECT
  campaign_name,
  DATE(send_time) AS send_date,
  sends, unique_opens,
  ROUND(open_rate_pct, 1) AS open_rate_pct,
  unique_clicks,
  ROUND(click_rate_pct, 2) AS click_rate_pct,
  unsubscribes, revenue
FROM `mine-and-yours-analytics.final_reporting.fact_klaviyo_campaigns`
ORDER BY send_date DESC
```
Visualization: **Table**

---
**Name:** `Avg Email Open Rate`
**Description:** `Average open rate across all Klaviyo email campaigns`
```sql
SELECT ROUND(AVG(open_rate_pct), 1) AS avg_open_rate
FROM `mine-and-yours-analytics.final_reporting.fact_klaviyo_campaigns`
```
Visualization: **Number** | Suffix: `%`

---
**Name:** `Avg Email Click Rate`
**Description:** `Average click-through rate across all Klaviyo email campaigns`
```sql
SELECT ROUND(AVG(click_rate_pct), 2) AS avg_click_rate
FROM `mine-and-yours-analytics.final_reporting.fact_klaviyo_campaigns`
```
Visualization: **Number** | Suffix: `%`

---
**Name:** `Total Email Sends`
**Description:** `Total number of emails sent across all campaigns`
```sql
SELECT SUM(sends) AS total_sends
FROM `mine-and-yours-analytics.final_reporting.fact_klaviyo_campaigns`
```
Visualization: **Number**

---

## 8. SHIPPING / OPS SCORECARD

### Tab: Overview

---
**Name:** `Shipping % of Sales MTD`
**Description:** `Shipping revenue as a percentage of total net sales for current month`
```sql
SELECT ROUND(
  SUM(shipping_revenue) / NULLIF(SUM(net_sales), 0) * 100, 1
) AS shipping_pct
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
Visualization: **Number** | Suffix: `%`

---
**Name:** `Avg Order Processing Time`
**Description:** `Average hours between order creation and processing in last 30 days`
```sql
SELECT ROUND(
  AVG(TIMESTAMP_DIFF(
    TIMESTAMP(order_processed_ts),
    TIMESTAMP(order_created_ts), HOUR
  )), 1
) AS avg_processing_hrs
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND order_processed_ts IS NOT NULL AND order_created_ts IS NOT NULL
```
Visualization: **Number** | Suffix: ` hrs`

---
**Name:** `Orders by Channel MTD`
**Description:** `Order count, net sales and shipping revenue split by channel for current month`
```sql
SELECT
  channel,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(net_sales), 2) AS net_sales,
  ROUND(SUM(shipping_revenue), 2) AS shipping_revenue
FROM `mine-and-yours-analytics.final_reporting.fact_orders_v2`
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY channel ORDER BY orders DESC
```
Visualization: **Table**

---
**Name:** `Shipping Revenue Trend (30 days)`
**Description:** `Daily shipping revenue and its percentage of net sales over last 30 days`
```sql
SELECT
  order_date,
  ROUND(SUM(shipping_revenue), 2) AS shipping_revenue,
  ROUND(SUM(net_sales), 2) AS net_sales,
  ROUND(SUM(shipping_revenue) / NULLIF(SUM(net_sales), 0) * 100, 1) AS shipping_pct
FROM `mine-and-yours-analytics.final_reporting.fact_daily_sales_v2`
WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY order_date ORDER BY order_date
```
Visualization: **Line**

---
**Name:** `Refunds by Channel MTD`
**Description:** `Number of refund orders and total refund value split by channel`
```sql
SELECT
  channel,
  COUNT(DISTINCT order_id) AS refund_orders,
  ROUND(SUM(refund_subtotal), 2) AS refund_value
FROM `mine-and-yours-analytics.final_reporting.fact_refunds_v2`
WHERE DATE_TRUNC(refund_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY channel ORDER BY refund_value DESC
```
Visualization: **Table**
