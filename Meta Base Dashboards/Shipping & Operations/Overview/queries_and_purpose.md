# Shipping & Operations — Overview Tab

**Purpose:** Order volume, shipping revenue and returns. Filters: Date Range · Channel · Store Location.

**Source views:** `fact_orders_v2`, `fact_daily_sales_v2`, `fact_refunds_v2`

---

## Shipping Revenue
```sql
SELECT ROUND(SUM(shipping_revenue), 2) AS shipping_revenue
FROM final_reporting.fact_orders_v2
WHERE {{order_date}} [[AND {{channel}}]] [[AND {{store_location}}]]
```

## Total Orders
```sql
SELECT COUNT(DISTINCT order_id) AS orders
FROM final_reporting.fact_orders_v2
WHERE {{order_date}} [[AND {{channel}}]] [[AND {{store_location}}]]
```

## Orders by Channel
```sql
SELECT channel, COUNT(DISTINCT order_id) AS orders
FROM final_reporting.fact_orders_v2
WHERE {{order_date}} [[AND {{store_location}}]]
GROUP BY channel
```

## Shipping Revenue by Day
```sql
SELECT order_date, ROUND(SUM(shipping_revenue), 2) AS shipping_revenue
FROM final_reporting.fact_daily_sales_v2
WHERE {{order_date}} [[AND {{channel}}]]
GROUP BY order_date ORDER BY order_date
```

## Returns by Channel
```sql
SELECT channel, COUNT(DISTINCT order_id) AS return_orders
FROM final_reporting.fact_refunds_v2
WHERE {{refund_date}} [[AND {{store_location}}]]
GROUP BY channel
```
