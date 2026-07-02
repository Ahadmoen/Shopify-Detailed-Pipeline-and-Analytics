# Inventory & Buying — Products Tab

**Purpose:** Shows each product's sales channel, store, revenue and margin once sold — answers "where was inventory sold". Inventory itself has no channel (unsold stock); this tab bridges inventory to sales.

**Source view:** `final_reporting.fact_product_sales_v2`

---

## Product Sales Table
```sql
SELECT
  order_date, product_title, sku, vendor,
  channel, store_location,
  units_sold, gross_revenue, cost, gross_profit, gross_margin_pct
FROM final_reporting.fact_product_sales_v2
WHERE {{order_date}} [[AND {{store_location}}]] [[AND {{channel}}]]
ORDER BY gross_revenue DESC
```
