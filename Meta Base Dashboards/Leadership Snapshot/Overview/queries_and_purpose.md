# Leadership Snapshot — Overview Tab

**Purpose:** High-level order and sales summary with channel and location breakdown. Date + Store Location filters. Number cards use Trend chart type for period comparison.

**Source view:** `final_reporting.fact_orders_v2`

---

## Orders
Total distinct orders for selected period.
```sql
SELECT COUNT(DISTINCT order_id) AS orders
FROM final_reporting.fact_orders_v2
WHERE {{order_date}} [[AND {{store_location}}]] [[AND {{channel}}]]
```

## Units Sold
```sql
SELECT SUM(total_units) AS units_sold
FROM final_reporting.fact_orders_v2
WHERE {{order_date}} [[AND {{store_location}}]] [[AND {{channel}}]]
```

## Net Sales
```sql
SELECT ROUND(SUM(net_sales), 2) AS net_sales
FROM final_reporting.fact_orders_v2
WHERE {{order_date}} [[AND {{store_location}}]] [[AND {{channel}}]]
```

## Refunded Units
```sql
SELECT SUM(refunded_units) AS refunded_units
FROM final_reporting.fact_refunds_v2
WHERE {{refund_date}} [[AND {{store_location}}]] [[AND {{channel}}]]
```

## Orders by Sales Channel (Pie)
```sql
SELECT channel, COUNT(DISTINCT order_id) AS orders
FROM final_reporting.fact_orders_v2
WHERE {{order_date}} [[AND {{store_location}}]]
GROUP BY channel
```

## Orders by Channel and Province (Table)
```sql
SELECT ship_province, channel, COUNT(DISTINCT order_id) AS orders
FROM final_reporting.fact_orders_v2
WHERE {{order_date}} [[AND {{store_location}}]]
GROUP BY ship_province, channel
ORDER BY orders DESC
```
