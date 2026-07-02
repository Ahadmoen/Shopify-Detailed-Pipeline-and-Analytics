# Inventory & Buying — Condition & Location Tab

**Purpose:** Quality mix and store distribution of current stock.

**Source view:** `final_reporting.fact_inventory_v2`

---

## Products by Condition Grade
```sql
SELECT condition_grade, COUNT(*) AS products
FROM final_reporting.fact_inventory_v2
WHERE condition_grade IS NOT NULL [[AND {{store_location}}]]
GROUP BY condition_grade ORDER BY products DESC
```

## Retail Value by Condition Grade
```sql
SELECT condition_grade, ROUND(SUM(retail_value), 2) AS retail_value
FROM final_reporting.fact_inventory_v2
WHERE condition_grade IS NOT NULL [[AND {{store_location}}]]
GROUP BY condition_grade
```

## Condition Grade Summary Table
```sql
SELECT
  condition_grade,
  COUNT(*) AS products,
  SUM(units_on_hand) AS units,
  ROUND(SUM(retail_value), 2) AS retail_value,
  ROUND(AVG(days_in_inventory), 0) AS avg_days_in_stock
FROM final_reporting.fact_inventory_v2
WHERE condition_grade IS NOT NULL [[AND {{store_location}}]]
GROUP BY condition_grade ORDER BY retail_value DESC
```
