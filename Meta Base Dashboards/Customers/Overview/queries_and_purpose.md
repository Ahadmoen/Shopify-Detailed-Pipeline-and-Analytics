# Customers — Overview Tab

**Purpose:** Customer segmentation and lifetime value. Filters: Date Range (customer created) · Store Location (preferred store) · Channel (preferred channel).

**Source view:** `final_reporting.fact_customers_v2`

---

## New vs Returning Customers
```sql
SELECT customer_type, COUNT(*) AS customers
FROM final_reporting.fact_customers_v2
WHERE orders_count > 0 [[AND {{customer_created_at}}]] [[AND {{store_location}}]] [[AND {{channel}}]]
GROUP BY customer_type
```

## Purchase Segments
```sql
SELECT purchase_segment, COUNT(*) AS customers
FROM final_reporting.fact_customers_v2
WHERE 1=1 [[AND {{customer_created_at}}]] [[AND {{store_location}}]] [[AND {{channel}}]]
GROUP BY purchase_segment
```

## Repeat Customers
```sql
SELECT COUNT(*) AS repeat_customers
FROM final_reporting.fact_customers_v2
WHERE purchase_segment = 'Repeat' [[AND {{store_location}}]] [[AND {{channel}}]]
```

## Average Customer LTV
```sql
SELECT ROUND(AVG(total_spent), 2) AS avg_ltv
FROM final_reporting.fact_customers_v2
WHERE orders_count > 0 [[AND {{store_location}}]] [[AND {{channel}}]]
```

## Top 20 Customers by Spend
```sql
SELECT
  CONCAT(first_name, ' ', last_name) AS customer,
  orders_count, ROUND(total_spent, 2) AS total_spent,
  ROUND(aov, 2) AS aov, store_location, channel
FROM final_reporting.fact_customers_v2
WHERE 1=1 [[AND {{store_location}}]] [[AND {{channel}}]]
ORDER BY total_spent DESC
LIMIT 20
```
