# Ecomm — KPIs Tab

**Purpose:** Online store performance. Filter: Date Range.

**Source view:** `final_reporting.fact_orders_v2` (channel = 'Ecomm')

---

## Ecomm Net Sales
```sql
SELECT ROUND(SUM(net_sales), 2) AS net_sales
FROM final_reporting.fact_orders_v2
WHERE channel = 'Ecomm' AND {{order_date}}
```

## Ecomm Orders
```sql
SELECT COUNT(DISTINCT order_id) AS orders
FROM final_reporting.fact_orders_v2
WHERE channel = 'Ecomm' AND {{order_date}}
```

## Ecomm AOV
```sql
SELECT ROUND(SUM(net_sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS aov
FROM final_reporting.fact_orders_v2
WHERE channel = 'Ecomm' AND {{order_date}}
```

## Ecomm Units Sold
```sql
SELECT SUM(total_units) AS units
FROM final_reporting.fact_orders_v2
WHERE channel = 'Ecomm' AND {{order_date}}
```

## Ecomm Gross Profit
```sql
SELECT ROUND(SUM(gross_profit), 2) AS gross_profit
FROM final_reporting.fact_orders_v2
WHERE channel = 'Ecomm' AND {{order_date}}
```

## Ecomm Return Orders
```sql
SELECT COUNT(DISTINCT order_id) AS return_orders
FROM final_reporting.fact_refunds_v2
WHERE channel = 'Ecomm' AND {{refund_date}}
```
