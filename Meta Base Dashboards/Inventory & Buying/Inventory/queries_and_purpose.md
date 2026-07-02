# Inventory & Buying — Inventory Tab

**Purpose:** Complete product list with cost, aging, condition, location and seller.

**Source view:** `final_reporting.fact_inventory_v2`

---

## Full Inventory Table
```sql
SELECT
  product_title, product_vendor, product_type,
  units_on_hand, retail_price, unit_cost, retail_value,
  contract_type, condition_grade, store_location,
  seller_name, buy_date, days_in_inventory, aging_bucket
FROM final_reporting.fact_inventory_v2
WHERE 1=1 [[AND {{snapshot_date}}]] [[AND {{store_location}}]] [[AND {{contract_type}}]]
ORDER BY retail_value DESC
```
