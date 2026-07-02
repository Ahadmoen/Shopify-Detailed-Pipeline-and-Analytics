# Supplier & Seller — Overview Tab

**Purpose:** Supplier volume, contract mix and buyer overlap. Filters: Date Range (last_buy_date) · Contract Type · Store Location · Channel.

**Source view:** `final_reporting.fact_seller`

---

## Items Supplied by Contract Type
```sql
SELECT contract_type, SUM(total_items_supplied) AS items
FROM final_reporting.fact_seller
WHERE 1=1 [[AND {{last_buy_date}}]] [[AND {{store_location}}]] [[AND {{channel}}]]
GROUP BY contract_type
```

## Top 20 Sellers by Units
```sql
SELECT seller_name, SUM(total_items_supplied) AS items_supplied, store_location
FROM final_reporting.fact_seller
WHERE 1=1 [[AND {{last_buy_date}}]] [[AND {{store_location}}]]
GROUP BY seller_name, store_location
ORDER BY items_supplied DESC
LIMIT 20
```

## Sellers Who Also Buy (Table)
```sql
SELECT
  seller_name, total_items_supplied, contract_type, store_location,
  buyer_orders_count, ROUND(buyer_total_spent, 2) AS buyer_total_spent
FROM final_reporting.fact_seller
WHERE is_also_buyer = TRUE [[AND {{store_location}}]]
ORDER BY buyer_total_spent DESC
```

## Sellers by Contract Type
```sql
SELECT contract_type, COUNT(DISTINCT seller_name) AS sellers
FROM final_reporting.fact_seller
WHERE 1=1 [[AND {{store_location}}]]
GROUP BY contract_type
```
