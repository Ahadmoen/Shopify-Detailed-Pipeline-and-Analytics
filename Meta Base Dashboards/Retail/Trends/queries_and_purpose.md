# Retail — Trends Tab

**Source views:** `fact_daily_sales_v2`, `fact_orders_v2`

---

## Retail Sales by Day
```sql
SELECT order_date, ROUND(SUM(net_sales), 2) AS net_sales
FROM final_reporting.fact_daily_sales_v2
WHERE channel = 'Retail' AND {{order_date}} [[AND {{store_location}}]]
GROUP BY order_date ORDER BY order_date
```

## Retail Orders by Day
```sql
SELECT order_date, COUNT(DISTINCT order_id) AS orders
FROM final_reporting.fact_orders_v2
WHERE channel = 'Retail' AND {{order_date}} [[AND {{store_location}}]]
GROUP BY order_date ORDER BY order_date
```

## Retail vs Ecomm Sales
```sql
SELECT order_date, channel, ROUND(SUM(net_sales), 2) AS net_sales
FROM final_reporting.fact_daily_sales_v2
WHERE channel IN ('Retail', 'Ecomm') AND {{order_date}}
GROUP BY order_date, channel ORDER BY order_date
```
