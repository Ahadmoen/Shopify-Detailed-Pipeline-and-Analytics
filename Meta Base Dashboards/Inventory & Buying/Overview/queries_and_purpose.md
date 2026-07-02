# Inventory & Buying — Overview Tab

**Purpose:** Summary of current stock value and distribution. "As of Date" single-date filter on snapshot_date; Store Location and Contract Type filters.

**Source view:** `final_reporting.fact_inventory_v2`

---

## Units on Hand
```sql
SELECT SUM(units_on_hand) AS units_on_hand
FROM final_reporting.fact_inventory_v2
WHERE 1=1 [[AND {{snapshot_date}}]] [[AND {{store_location}}]] [[AND {{contract_type}}]]
```

## On-Hand Retail Value
```sql
SELECT ROUND(SUM(retail_value), 2) AS retail_value
FROM final_reporting.fact_inventory_v2
WHERE 1=1 [[AND {{snapshot_date}}]] [[AND {{store_location}}]] [[AND {{contract_type}}]]
```

## On-Hand Cost (excl. consignment)
```sql
SELECT ROUND(SUM(cost_excl_consignment), 2) AS cost
FROM final_reporting.fact_inventory_v2
WHERE 1=1 [[AND {{snapshot_date}}]] [[AND {{store_location}}]]
```

## % Consignment in Stock
```sql
SELECT ROUND(COUNTIF(is_consignment) / COUNT(*) * 100, 1) AS pct_consignment
FROM final_reporting.fact_inventory_v2
WHERE 1=1 [[AND {{snapshot_date}}]] [[AND {{store_location}}]]
```

## Units by Location
```sql
SELECT store_location, SUM(units_on_hand) AS units
FROM final_reporting.fact_inventory_v2
WHERE store_location IS NOT NULL [[AND {{snapshot_date}}]]
GROUP BY store_location ORDER BY units DESC
```
