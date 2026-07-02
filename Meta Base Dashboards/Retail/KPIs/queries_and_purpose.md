# Retail — KPIs Tab

**Purpose:** In-store POS performance. Filters: Date Range · Store Location.

**Source view:** `final_reporting.fact_orders_v2` (channel = 'Retail')

---

## Retail Net Sales
```sql
SELECT ROUND(SUM(net_sales), 2) AS net_sales
FROM final_reporting.fact_orders_v2
WHERE channel = 'Retail' AND {{order_date}} [[AND {{store_location}}]]
```

## Retail Gross Profit
```sql
SELECT ROUND(SUM(gross_profit), 2) AS gross_profit
FROM final_reporting.fact_orders_v2
WHERE channel = 'Retail' AND {{order_date}} [[AND {{store_location}}]]
```

## Retail AOV
```sql
SELECT ROUND(SUM(net_sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS aov
FROM final_reporting.fact_orders_v2
WHERE channel = 'Retail' AND {{order_date}} [[AND {{store_location}}]]
```

## Retail Orders
```sql
SELECT COUNT(DISTINCT order_id) AS orders
FROM final_reporting.fact_orders_v2
WHERE channel = 'Retail' AND {{order_date}} [[AND {{store_location}}]]
```

## Retail Units Sold
```sql
SELECT SUM(total_units) AS units
FROM final_reporting.fact_orders_v2
WHERE channel = 'Retail' AND {{order_date}} [[AND {{store_location}}]]
```

## Retail Return Orders
```sql
SELECT COUNT(DISTINCT order_id) AS return_orders
FROM final_reporting.fact_refunds_v2
WHERE channel = 'Retail' AND {{refund_date}} [[AND {{store_location}}]]
```
