-- fact_customers_v2
-- Customer snapshot with segments, plus preferred store & channel from order history.

CREATE OR REPLACE VIEW final_reporting.fact_customers_v2 AS

WITH latest_customers AS (
  SELECT *
  FROM (
    SELECT *,
      ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY customer_updated_at DESC
      ) AS rn
    FROM raw_shopify.shopify_customers
    WHERE customer_id IS NOT NULL
  )
  WHERE rn = 1
),

customer_orders AS (
  SELECT
    order_customer_id,
    ARRAY_AGG(order_location_name IGNORE NULLS ORDER BY date DESC LIMIT 1)[SAFE_OFFSET(0)] AS preferred_store,
    ARRAY_AGG(
      CASE
        WHEN order_app_name = 'Point of Sale'           THEN 'Retail'
        WHEN order_app_name IN ('Online Store', 'Shop') THEN 'Ecomm'
        WHEN order_app_name = 'Draft Orders'            THEN 'Draft'
        WHEN order_app_name = '3890849'                 THEN 'Gorgias'
        ELSE 'Other'
      END
      IGNORE NULLS ORDER BY date DESC LIMIT 1
    )[SAFE_OFFSET(0)]                                                                        AS preferred_channel
  FROM (
    SELECT *
    FROM raw_shopify.shopify_orders
    WHERE order_customer_id IS NOT NULL
      AND LOWER(order_financial_status) != 'cancelled'
      AND LOWER(COALESCE(order_test, 'false')) = 'false'
    QUALIFY ROW_NUMBER() OVER (
      PARTITION BY order_id
      ORDER BY
        CASE WHEN order_location_name IS NOT NULL THEN 0 ELSE 1 END,
        date DESC
    ) = 1
  )
  GROUP BY order_customer_id
)

SELECT
  CAST(c.customer_id AS STRING)                                        AS customer_id,
  c.customer_first_name                                                AS first_name,
  c.customer_last_name                                                 AS last_name,
  c.customer_created_at,
  c.customer_updated_at,
  c.customer_default_address_city                                      AS city,
  c.customer_default_address_country                                   AS country,
  c.customer_default_address_country_code                              AS country_code,
  SAFE_CAST(c.customer_orders_count AS INT64)                         AS orders_count,
  SAFE_CAST(c.customer_total_spent AS FLOAT64)                        AS total_spent,
  SAFE_CAST(c.customer_aov AS FLOAT64)                                AS aov,
  CASE
    WHEN LOWER(CAST(c.customer_is_returning AS STRING)) = 'true'      THEN 'Returning'
    ELSE 'New'
  END                                                                  AS customer_type,
  CASE
    WHEN SAFE_CAST(c.customer_orders_count AS INT64) = 0             THEN 'No Orders'
    WHEN SAFE_CAST(c.customer_orders_count AS INT64) = 1             THEN 'One-time'
    WHEN SAFE_CAST(c.customer_orders_count AS INT64) >= 2            THEN 'Repeat'
  END                                                                  AS purchase_segment,
  o.preferred_store                                                    AS store_location,
  o.preferred_channel                                                  AS channel
FROM latest_customers c
LEFT JOIN customer_orders o
  ON CAST(c.customer_id AS STRING) = o.order_customer_id;
