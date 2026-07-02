-- fact_product_sales_v2
-- Line-item product sales with cost joined from products, margin, channel, store.

CREATE OR REPLACE VIEW final_reporting.fact_product_sales_v2 AS

WITH latest_costs AS (
  SELECT
    product_id,
    SAFE_CAST(product_variant_inventory_item_cost AS FLOAT64) AS unit_cost
  FROM raw_shopify.shopify_products
  WHERE product_id IS NOT NULL
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY product_id
    ORDER BY product_updated_at_datetime DESC
  ) = 1
)

SELECT
  DATE(DATETIME(TIMESTAMP(o.order_created_at), 'America/Vancouver')) AS order_date,
  CAST(o.line_item__product_id AS STRING)                             AS product_id,
  o.line_item__sku                                                    AS sku,
  o.line_item__title                                                  AS product_title,
  o.line_item__vendor                                                 AS vendor,
  CASE
    WHEN o.order_app_name = 'Point of Sale'           THEN 'Retail'
    WHEN o.order_app_name IN ('Online Store', 'Shop') THEN 'Ecomm'
    WHEN o.order_app_name = 'Draft Orders'            THEN 'Draft'
    WHEN o.order_app_name = '3890849'                 THEN 'Gorgias'
    ELSE 'Other'
  END                                                                 AS channel,
  o.order_shipping_address_country                                    AS ship_country,
  o.order_shipping_address_province                                   AS ship_province,
  o.order_location_name                                               AS store_location,
  SUM(SAFE_CAST(o.line_item__quantity AS FLOAT64))                   AS units_sold,
  ROUND(SUM(
    SAFE_CAST(o.line_item__price AS FLOAT64) *
    SAFE_CAST(o.line_item__quantity AS FLOAT64)
  ), 2)                                                               AS gross_revenue,
  ROUND(SUM(SAFE_CAST(o.line_item__total_discount AS FLOAT64)), 2)   AS total_line_discounts,
  ROUND(SUM(
    COALESCE(c.unit_cost, SAFE_CAST(o.line_item__variant_unit_cost AS FLOAT64), 0) *
    SAFE_CAST(o.line_item__quantity AS FLOAT64)
  ), 2)                                                               AS cost,
  ROUND(SUM(
    (SAFE_CAST(o.line_item__price AS FLOAT64) -
     COALESCE(c.unit_cost, SAFE_CAST(o.line_item__variant_unit_cost AS FLOAT64), 0)) *
    SAFE_CAST(o.line_item__quantity AS FLOAT64)
  ), 2)                                                               AS gross_profit,
  ROUND(SAFE_DIVIDE(
    SUM((SAFE_CAST(o.line_item__price AS FLOAT64) -
         COALESCE(c.unit_cost, SAFE_CAST(o.line_item__variant_unit_cost AS FLOAT64), 0)) *
        SAFE_CAST(o.line_item__quantity AS FLOAT64)),
    SUM(SAFE_CAST(o.line_item__price AS FLOAT64) * SAFE_CAST(o.line_item__quantity AS FLOAT64))
  ) * 100, 1)                                                         AS gross_margin_pct
FROM (
  SELECT *
  FROM raw_shopify.shopify_orders
  WHERE line_item__id IS NOT NULL
    AND line_item__id != ''
    AND line_item__product_id IS NOT NULL
    AND LOWER(COALESCE(order_test, 'false')) = 'false'
    AND LOWER(order_financial_status) != 'cancelled'
    AND LOWER(COALESCE(line_item__title, '')) NOT IN ('gift card', 'paper bag', '')
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id, line_item__id
    ORDER BY
      CASE WHEN order_location_name IS NOT NULL THEN 0 ELSE 1 END,
      order_created_at DESC
  ) = 1
) o
LEFT JOIN latest_costs c
  ON CAST(o.line_item__product_id AS STRING) = CAST(c.product_id AS STRING)
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9;
