# Ecomm — Trends Tab

**Source views:** `fact_daily_sales_v2`, `fact_orders_v2`

---

## Ecomm Sales by Day
```sql
SELECT order_date, ROUND(SUM(net_sales), 2) AS net_sales
FROM final_reporting.fact_daily_sales_v2
WHERE channel = 'Ecomm' AND {{order_date}}
GROUP BY order_date ORDER BY order_date
```

## Ecomm Orders by Day
```sql
SELECT order_date, COUNT(DISTINCT order_id) AS orders
FROM final_reporting.fact_orders_v2
WHERE channel = 'Ecomm' AND {{order_date}}
GROUP BY order_date ORDER BY order_date
```

## Sales by UTM Source
```sql
SELECT COALESCE(utm_source, '(none)') AS utm_source, ROUND(SUM(net_sales), 2) AS net_sales
FROM final_reporting.fact_orders_v2
WHERE channel = 'Ecomm' AND {{order_date}}
GROUP BY utm_source ORDER BY net_sales DESC
```
