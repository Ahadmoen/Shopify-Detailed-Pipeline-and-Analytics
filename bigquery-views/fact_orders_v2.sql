-- fact_orders_v2
-- Order-level view: one row per order, deduped, with COGS from products,
-- Vancouver timezone dates, channel + store location mapping, customer id.

CREATE OR REPLACE VIEW final_reporting.fact_orders_v2 AS

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
),

order_level AS (
  SELECT
    order_id, order_name,
    DATE(DATETIME(TIMESTAMP(order_created_at), 'America/Vancouver')) AS order_date,
    order_currency,
    order_app_name                                    AS sales_channel,
    CASE
      WHEN order_app_name = 'Point of Sale'           THEN 'Retail'
      WHEN order_app_name IN ('Online Store', 'Shop') THEN 'Ecomm'
      WHEN order_app_name = 'Draft Orders'            THEN 'Draft'
      WHEN order_app_name = '3890849'                 THEN 'Gorgias'
      ELSE 'Other'
    END                                               AS channel,
    LOWER(order_financial_status)                     AS financial_status,
    order_shipping_address_country                    AS ship_country,
    order_shipping_address_province                   AS ship_province,
    order_location_id                                 AS store_location_id,
    order_location_name                               AS store_location,
    order_customer_id,
    order_created_at                                  AS order_created_ts,
    order_processed_at                                AS order_processed_ts,
    SAFE_CAST(order_net_sales AS FLOAT64)             AS net_sales,
    SAFE_CAST(order_subtotal_price AS FLOAT64)        AS subtotal_revenue,
    SAFE_CAST(order_total_price AS FLOAT64)           AS gross_revenue,
    SAFE_CAST(order_total_discounts AS FLOAT64)       AS total_discounts,
    SAFE_CAST(order_shipping_price AS FLOAT64)        AS shipping_revenue,
    SAFE_CAST(order_total_tax_amount AS FLOAT64)      AS total_tax,
    order_customer_last_visit_utm_source              AS utm_source,
    order_customer_last_visit_utm_medium              AS utm_medium,
    order_customer_last_visit_utm_campaign            AS utm_campaign,
    year, week, year_month
  FROM raw_shopify.shopify_orders
  WHERE LOWER(COALESCE(order_test, 'false')) = 'false'
    AND LOWER(order_financial_status) != 'cancelled'
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY
      CASE WHEN order_location_name IS NOT NULL THEN 0 ELSE 1 END,
      date DESC
  ) = 1
),

line_items AS (
  SELECT
    o.order_id,
    SUM(SAFE_CAST(o.line_item__quantity AS FLOAT64))    AS total_units,
    SUM(
      SAFE_CAST(o.line_item__quantity AS FLOAT64) *
      COALESCE(c.unit_cost, SAFE_CAST(o.line_item__variant_unit_cost AS FLOAT64), 0)
    )                                                   AS cogs
  FROM (
    SELECT *
    FROM raw_shopify.shopify_orders
    WHERE line_item__id IS NOT NULL
      AND line_item__id != ''
      AND LOWER(order_financial_status) != 'cancelled'
      AND LOWER(COALESCE(order_test, 'false')) = 'false'
    QUALIFY ROW_NUMBER() OVER (
      PARTITION BY order_id, line_item__id
      ORDER BY
        CASE WHEN order_location_name IS NOT NULL THEN 0 ELSE 1 END,
        order_created_at DESC
    ) = 1
  ) o
  LEFT JOIN latest_costs c
    ON CAST(o.line_item__product_id AS STRING) = CAST(c.product_id AS STRING)
  GROUP BY o.order_id
)

SELECT
  o.*,
  COALESCE(l.total_units, 0)                                   AS total_units,
  COALESCE(l.cogs, 0)                                          AS cogs,
  o.net_sales - COALESCE(l.cogs, 0)                            AS gross_profit,
  SAFE_DIVIDE(o.net_sales - COALESCE(l.cogs, 0), o.net_sales)  AS gross_margin_pct
FROM order_level o
LEFT JOIN line_items l ON o.order_id = l.order_id;
