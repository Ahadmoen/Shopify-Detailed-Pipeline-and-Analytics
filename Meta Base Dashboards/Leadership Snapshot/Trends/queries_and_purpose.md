# Leadership Snapshot — Trends Tab

**Purpose:** Daily trend lines for all key metrics over any selected date range.

**Source views:** `fact_daily_sales_v2`, `fact_orders_v2`, `fact_refunds_v2`

---

## Net Sales Daily Trend
```sql
SELECT order_date, ROUND(SUM(net_sales), 2) AS net_sales
FROM final_reporting.fact_daily_sales_v2
WHERE {{order_date}}
GROUP BY order_date ORDER BY order_date
```

## Net Sales by Channel Over Time
```sql
SELECT order_date, channel, ROUND(SUM(net_sales), 2) AS net_sales
FROM final_reporting.fact_daily_sales_v2
WHERE {{order_date}}
GROUP BY order_date, channel ORDER BY order_date
```

## Orders by Day
```sql
SELECT order_date, COUNT(DISTINCT order_id) AS orders
FROM final_reporting.fact_orders_v2
WHERE {{order_date}}
GROUP BY order_date ORDER BY order_date
```

## AOV by Day
```sql
SELECT order_date, ROUND(SUM(net_sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS aov
FROM final_reporting.fact_orders_v2
WHERE {{order_date}}
GROUP BY order_date ORDER BY order_date
```

## Units Sold by Day
```sql
SELECT order_date, SUM(total_units) AS units
FROM final_reporting.fact_orders_v2
WHERE {{order_date}}
GROUP BY order_date ORDER BY order_date
```

## Gross Margin % by Day
```sql
SELECT order_date, ROUND(SUM(gross_profit) / NULLIF(SUM(net_sales), 0) * 100, 1) AS margin_pct
FROM final_reporting.fact_orders_v2
WHERE {{order_date}}
GROUP BY order_date ORDER BY order_date
```

## Returns by Day
```sql
SELECT refund_date, COUNT(DISTINCT order_id) AS return_orders
FROM final_reporting.fact_refunds_v2
WHERE {{refund_date}}
GROUP BY refund_date ORDER BY refund_date
```

## Refunded Value by Day
```sql
SELECT refund_date, ROUND(SUM(total_refunded), 2) AS refunded_value
FROM final_reporting.fact_refunds_v2
WHERE {{refund_date}}
GROUP BY refund_date ORDER BY refund_date
```
