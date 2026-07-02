-- fact_inventory_v2
-- Point-in-time inventory snapshot with aging, condition and store location
-- (location JSON array from metafield cleaned via REGEXP_EXTRACT).

CREATE OR REPLACE VIEW final_reporting.fact_inventory_v2 AS

WITH latest_products AS (
  SELECT *
  FROM (
    SELECT *,
      ROW_NUMBER() OVER (
        PARTITION BY product_id
        ORDER BY product_updated_at_datetime DESC
      ) AS rn
    FROM raw_shopify.shopify_products
    WHERE product_id IS NOT NULL
      AND LOWER(product_status) = 'active'
  )
  WHERE rn = 1
),
latest_metafields AS (
  SELECT *
  FROM (
    SELECT *,
      ROW_NUMBER() OVER (
        PARTITION BY product_id, product_metafield_namespace, product_metafield_key
        ORDER BY product_metafield_update_at DESC
      ) AS rn
    FROM raw_shopify.shopify_product_metafields
    WHERE product_id IS NOT NULL
  )
  WHERE rn = 1
),
metafields_pivot AS (
  SELECT
    product_id,
    MAX(CASE WHEN product_metafield_namespace = 'buy'    AND product_metafield_key = 'contract_type' THEN product_metafield_value END) AS contract_type,
    MAX(CASE WHEN product_metafield_namespace = 'buy'    AND product_metafield_key = 'date'          THEN product_metafield_value END) AS buy_date,
    MAX(CASE WHEN product_metafield_namespace = 'buy'    AND product_metafield_key = 'seller_name'   THEN product_metafield_value END) AS seller_name,
    MAX(CASE WHEN product_metafield_namespace = 'buy'    AND product_metafield_key = 'msrp'          THEN product_metafield_value END) AS msrp,
    MAX(CASE WHEN product_metafield_namespace = 'custom' AND product_metafield_key = 'condition'     THEN product_metafield_value END) AS condition_grade,
    REGEXP_EXTRACT(
      MAX(CASE WHEN product_metafield_namespace = 'custom' AND product_metafield_key = 'location' THEN product_metafield_value END),
      r'"([^"]+)"'
    )                                                                                               AS store_location
  FROM latest_metafields
  GROUP BY product_id
)
SELECT
  CAST(p.product_id AS STRING)                                                                     AS product_id,
  p.product_title,
  p.product_type,
  p.product_vendor,
  p.product_status,
  p.product_tags,
  p.date                                                                                           AS snapshot_date,
  SAFE_CAST(p.product_inventory_quantity AS INT64)                                                AS units_on_hand,
  SAFE_CAST(p.product_price AS FLOAT64)                                                           AS retail_price,
  SAFE_CAST(p.product_variant_inventory_item_cost AS FLOAT64)                                     AS unit_cost,
  ROUND(SAFE_CAST(p.product_price AS FLOAT64) *
    SAFE_CAST(p.product_inventory_quantity AS INT64), 2)                                          AS retail_value,
  ROUND(SAFE_CAST(p.product_variant_inventory_item_cost AS FLOAT64) *
    SAFE_CAST(p.product_inventory_quantity AS INT64), 2)                                          AS cost_value,
  CASE
    WHEN LOWER(m.contract_type) != 'consignment'
    THEN ROUND(SAFE_CAST(p.product_variant_inventory_item_cost AS FLOAT64) *
      SAFE_CAST(p.product_inventory_quantity AS INT64), 2)
    ELSE 0
  END                                                                                              AS cost_excl_consignment,
  m.contract_type,
  CASE WHEN LOWER(m.contract_type) = 'consignment' THEN TRUE ELSE FALSE END                       AS is_consignment,
  m.buy_date,
  m.seller_name,
  SAFE_CAST(m.msrp AS FLOAT64)                                                                    AS msrp,
  m.condition_grade,
  m.store_location,
  DATE_DIFF(p.date, SAFE.PARSE_DATE('%Y-%m-%d', m.buy_date), DAY)                                AS days_in_inventory,
  CASE
    WHEN DATE_DIFF(p.date, SAFE.PARSE_DATE('%Y-%m-%d', m.buy_date), DAY) <= 30                   THEN '0-30 days'
    WHEN DATE_DIFF(p.date, SAFE.PARSE_DATE('%Y-%m-%d', m.buy_date), DAY) <= 60                   THEN '31-60 days'
    WHEN DATE_DIFF(p.date, SAFE.PARSE_DATE('%Y-%m-%d', m.buy_date), DAY) <= 90                   THEN '61-90 days'
    WHEN DATE_DIFF(p.date, SAFE.PARSE_DATE('%Y-%m-%d', m.buy_date), DAY) <= 180                  THEN '91-180 days'
    ELSE '180+ days'
  END                                                                                              AS aging_bucket,
  p.product_created_at_datetime,
  p.product_updated_at_datetime
FROM latest_products p
LEFT JOIN metafields_pivot m
  ON CAST(p.product_id AS STRING) = CAST(m.product_id AS STRING);
