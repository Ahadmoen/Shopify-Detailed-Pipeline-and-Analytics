-- fact_refunds_v2
-- Refund records deduped, with channel + store location from parent order.

CREATE OR REPLACE VIEW final_reporting.fact_refunds_v2 AS
WITH refund_deduped AS (
  SELECT *,
    REGEXP_EXTRACT(order_refunds, r'/(\d+)$') AS refund_id
  FROM raw_shopify.shopify_refunds
  WHERE order_id IS NOT NULL
    AND (
      SAFE_CAST(line_item__refunds_subtotal AS FLOAT64) > 0
      OR SAFE_CAST(order_refund_discrepancy_amount AS FLOAT64) != 0
      OR SAFE_CAST(order_total_shipping_refunded_price AS FLOAT64) != 0
    )
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY
      order_id,
      COALESCE(order_refunds, 'NO_REFUND'),
      COALESCE(CAST(line_item__refunds_subtotal AS STRING), '0'),
      COALESCE(CAST(line_item__refunds_quantity AS STRING), '0')
    ORDER BY date DESC
  ) = 1
),

order_info AS (
  SELECT
    order_id,
    order_app_name,
    CASE
      WHEN order_app_name = 'Point of Sale'           THEN 'Retail'
      WHEN order_app_name IN ('Online Store', 'Shop') THEN 'Ecomm'
      WHEN order_app_name = 'Draft Orders'            THEN 'Draft'
      WHEN order_app_name = '3890849'                 THEN 'Gorgias'
      ELSE 'Other'
    END                                               AS channel,
    LOWER(order_financial_status)                     AS financial_status,
    order_currency,
    order_shipping_address_country                    AS ship_country,
    order_shipping_address_province                   AS ship_province,
    order_location_name                               AS store_location
  FROM raw_shopify.shopify_orders
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY
      CASE WHEN order_location_name IS NOT NULL THEN 0 ELSE 1 END,
      order_created_at DESC
  ) = 1
)

SELECT
  DATE(DATETIME(TIMESTAMP(r.date), 'America/Vancouver'))              AS refund_date,
  r.refund_id,
  r.order_id,
  r.order_name,
  o.channel,
  o.financial_status,
  o.order_currency                                                     AS currency,
  o.ship_country,
  o.ship_province,
  o.store_location,
  SAFE_CAST(r.line_item__refunds_quantity AS FLOAT64)                  AS refunded_units,
  ROUND(SAFE_CAST(r.line_item__refunds_subtotal AS FLOAT64), 2)        AS refund_subtotal,
  ROUND(SAFE_CAST(r.order_total_shipping_refunded_price AS FLOAT64), 2) AS refund_shipping,
  ROUND(SAFE_CAST(r.order_refund_discrepancy_amount AS FLOAT64), 2)    AS refund_discrepancy,
  ROUND(SAFE_CAST(r.line_item__refunds_total_tax AS FLOAT64), 2)       AS refund_tax,
  ROUND(
    COALESCE(SAFE_CAST(r.line_item__refunds_subtotal AS FLOAT64), 0) +
    COALESCE(SAFE_CAST(r.order_refund_discrepancy_amount AS FLOAT64), 0) +
    COALESCE(SAFE_CAST(r.order_total_shipping_refunded_price AS FLOAT64), 0)
  , 2)                                                                  AS total_refunded,
  r.week,
  r.year,
  r.year_month
FROM refund_deduped r
LEFT JOIN order_info o ON r.order_id = o.order_id;
