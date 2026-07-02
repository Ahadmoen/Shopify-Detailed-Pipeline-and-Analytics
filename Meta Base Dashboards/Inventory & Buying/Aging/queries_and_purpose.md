# Inventory & Buying — Aging Tab

**Purpose:** Identifies slow-moving and at-risk inventory via aging buckets computed buy_date → snapshot_date.

**Source view:** `final_reporting.fact_inventory_v2`

---

## % Aging Over 90 Days
```sql
SELECT ROUND(COUNTIF(days_in_inventory > 90) / COUNT(*) * 100, 1) AS pct_over_90
FROM final_reporting.fact_inventory_v2
WHERE days_in_inventory IS NOT NULL [[AND {{store_location}}]] [[AND {{contract_type}}]]
```

## Products by Aging Bucket
```sql
SELECT aging_bucket, COUNT(*) AS products
FROM final_reporting.fact_inventory_v2
WHERE days_in_inventory IS NOT NULL [[AND {{store_location}}]]
GROUP BY aging_bucket
ORDER BY CASE aging_bucket
  WHEN '0-30 days' THEN 1 WHEN '31-60 days' THEN 2
  WHEN '61-90 days' THEN 3 WHEN '91-180 days' THEN 4 ELSE 5 END
```

## Retail Value by Aging Bucket
```sql
SELECT aging_bucket, ROUND(SUM(retail_value), 2) AS retail_value
FROM final_reporting.fact_inventory_v2
WHERE days_in_inventory IS NOT NULL [[AND {{store_location}}]]
GROUP BY aging_bucket
```

## Dead Stock Units (180+ days)
```sql
SELECT SUM(units_on_hand) AS dead_stock_units
FROM final_reporting.fact_inventory_v2
WHERE aging_bucket = '180+ days' [[AND {{store_location}}]]
```

## Avg Days in Inventory
```sql
SELECT ROUND(AVG(days_in_inventory), 0) AS avg_days
FROM final_reporting.fact_inventory_v2
WHERE days_in_inventory IS NOT NULL [[AND {{store_location}}]]
```
