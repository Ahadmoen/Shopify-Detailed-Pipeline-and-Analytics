-- fact_seller
-- Consignment/buyout sellers with items supplied, store location (cleaned from
-- JSON array metafield), channel of sold items, and buyer overlap.

CREATE OR REPLACE VIEW final_reporting.fact_seller AS

WITH seller_products AS (
  SELECT
    product_id,
    MAX(CASE WHEN product_metafield_key = 'seller_name'     THEN product_metafield_value END) AS seller_name,
    MAX(CASE WHEN product_metafield_key = 'contract_type'   THEN product_metafield_value END) AS contract_type,
    MAX(CASE WHEN product_metafield_key = 'date'            THEN product_metafield_value END) AS buy_date,
    MAX(CASE WHEN product_metafield_key = 'msrp'            THEN product_metafield_value END) AS msrp,
    MAX(CASE WHEN product_metafield_key = 'condition_notes' THEN product_metafield_value END) AS condition_notes
  FROM raw_shopify.shopify_product_metafields
  WHERE product_metafield_namespace = 'buy'
  GROUP BY product_id
),

seller_with_location AS (
  SELECT
    sp.product_id,
    sp.seller_name,
    sp.contract_type,
    sp.buy_date,
    REGEXP_EXTRACT(loc.location, r'"([^"]+)"') AS store_location
  FROM seller_products sp
  LEFT JOIN (
    SELECT
      product_id,
      MAX(CASE WHEN product_metafield_key = 'location' THEN product_metafield_value END) AS location
    FROM raw_shopify.shopify_product_metafields
    WHERE product_metafield_namespace = 'custom'
    GROUP BY product_id
  ) loc ON sp.product_id = loc.product_id
  WHERE sp.seller_name IS NOT NULL AND sp.seller_name != ''
),

product_channel AS (
  SELECT
    product_id,
    channel
  FROM final_reporting.fact_product_sales_v2
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY product_id
    ORDER BY order_date DESC
  ) = 1
),

seller_summary AS (
  SELECT
    swl.seller_name,
    swl.contract_type,
    swl.store_location,
    pc.channel,
    COUNT(*)                                                    AS total_items_supplied,
    COUNTIF(swl.contract_type = 'consignment')                  AS consignment_items,
    COUNTIF(swl.contract_type = 'buyout')                       AS buyout_items,
    COUNTIF(swl.contract_type = 'store_credit')                 AS store_credit_items,
    MIN(swl.buy_date)                                           AS first_buy_date,
    MAX(swl.buy_date)                                           AS last_buy_date
  FROM seller_with_location swl
  LEFT JOIN product_channel pc
    ON CAST(swl.product_id AS STRING) = CAST(pc.product_id AS STRING)
  GROUP BY swl.seller_name, swl.contract_type, swl.store_location, pc.channel
),

consignment_customers AS (
  SELECT *
  FROM (
    SELECT *,
      ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY date DESC) AS rn
    FROM raw_shopify.shopify_customers
    WHERE LOWER(customer_tags) LIKE '%cognito-consignment%'
  )
  WHERE rn = 1
)

SELECT
  s.seller_name,
  s.contract_type,
  s.store_location,
  s.channel,
  s.total_items_supplied,
  s.consignment_items,
  s.buyout_items,
  s.store_credit_items,
  s.first_buy_date,
  s.last_buy_date,
  c.customer_id,
  c.customer_first_name,
  c.customer_last_name,
  SAFE_CAST(c.customer_orders_count AS INT64)     AS buyer_orders_count,
  SAFE_CAST(c.customer_total_spent AS FLOAT64)    AS buyer_total_spent,
  SAFE_CAST(c.customer_aov AS FLOAT64)            AS buyer_aov,
  CASE
    WHEN c.customer_id IS NOT NULL THEN TRUE
    ELSE FALSE
  END                                             AS is_also_buyer
FROM seller_summary s
LEFT JOIN consignment_customers c
  ON LOWER(TRIM(s.seller_name)) =
     LOWER(CONCAT(TRIM(c.customer_first_name), ' ', TRIM(c.customer_last_name)));
