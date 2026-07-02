# Leadership Snapshot — MTD KPIs Tab

**Purpose:** Current-month KPIs. Defaults to this month; date filter allows any period.

**Source views:** `fact_orders_v2`, `fact_inventory_v2`, `fact_refunds_v2`, `fact_product_sales_v2`

---

## Net Sales MTD
```sql
SELECT ROUND(SUM(net_sales), 2) AS net_sales_mtd
FROM final_reporting.fact_orders_v2
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```

## Gross Profit MTD
```sql
SELECT ROUND(SUM(gross_profit), 2) AS gross_profit_mtd
FROM final_reporting.fact_orders_v2
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```

## Gross Margin % MTD
```sql
SELECT ROUND(SUM(gross_profit) / NULLIF(SUM(net_sales), 0) * 100, 1) AS gross_margin_pct
FROM final_reporting.fact_orders_v2
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```

## AOV MTD
```sql
SELECT ROUND(SUM(net_sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS aov_mtd
FROM final_reporting.fact_orders_v2
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```

## Total Orders MTD
```sql
SELECT COUNT(DISTINCT order_id) AS orders_mtd
FROM final_reporting.fact_orders_v2
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```

## Total Units Sold MTD
```sql
SELECT SUM(total_units) AS units_mtd
FROM final_reporting.fact_orders_v2
WHERE DATE_TRUNC(order_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```

## Total Inventory Retail Value
```sql
SELECT ROUND(SUM(retail_value), 2) AS inventory_retail_value
FROM final_reporting.fact_inventory_v2
```

## Total Inventory Cost (excl. consignment)
```sql
SELECT ROUND(SUM(cost_excl_consignment), 2) AS inventory_cost
FROM final_reporting.fact_inventory_v2
```

## Sell-through Rate (30 days)
```sql
WITH sold AS (
  SELECT SUM(units_sold) AS units_sold
  FROM final_reporting.fact_product_sales_v2
  WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
),
stock AS (
  SELECT SUM(units_on_hand) AS units_on_hand
  FROM final_reporting.fact_inventory_v2
)
SELECT ROUND(s.units_sold / NULLIF(s.units_sold + k.units_on_hand, 0) * 100, 1) AS sell_through_pct
FROM sold s, stock k
```

## Return Orders MTD
```sql
SELECT COUNT(DISTINCT order_id) AS return_orders_mtd
FROM final_reporting.fact_refunds_v2
WHERE DATE_TRUNC(refund_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```

## Refunded Units MTD
```sql
SELECT SUM(refunded_units) AS refunded_units_mtd
FROM final_reporting.fact_refunds_v2
WHERE DATE_TRUNC(refund_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```

## Refunded Value MTD
```sql
SELECT ROUND(SUM(total_refunded), 2) AS refunded_value_mtd
FROM final_reporting.fact_refunds_v2
WHERE DATE_TRUNC(refund_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)
```
