-- fact_daily_sales_v2
-- Daily aggregated sales by channel, ship geography and store location.

CREATE OR REPLACE VIEW final_reporting.fact_daily_sales_v2 AS
SELECT
  DATE(DATETIME(TIMESTAMP(order_created_at), 'America/Vancouver')) AS order_date,
  CASE
    WHEN order_app_name = 'Point of Sale'           THEN 'Retail'
    WHEN order_app_name IN ('Online Store', 'Shop') THEN 'Ecomm'
    WHEN order_app_name = 'Draft Orders'            THEN 'Draft'
    WHEN order_app_name = '3890849'                 THEN 'Gorgias'
    ELSE 'Other'
  END                                                              AS channel,
  order_shipping_address_country                                   AS ship_country,
  order_shipping_address_province                                  AS ship_province,
  order_location_name                                              AS store_location,
  ROUND(SUM(SAFE_CAST(order_net_sales AS FLOAT64)), 2)            AS net_sales,
  ROUND(SUM(SAFE_CAST(order_total_discounts AS FLOAT64)), 2)      AS total_discounts,
  ROUND(SUM(SAFE_CAST(order_shipping_price AS FLOAT64)), 2)       AS shipping_revenue,
  ROUND(SUM(SAFE_CAST(order_total_price AS FLOAT64)), 2)          AS gross_revenue,
  SUM(SAFE_CAST(order_quantity AS FLOAT64))                       AS total_units,
  ROUND(SAFE_DIVIDE(
    SUM(SAFE_CAST(order_net_sales AS FLOAT64)),
    NULLIF(COUNT(DISTINCT order_id), 0)
  ), 2)                                                           AS aov
FROM (
  SELECT *
  FROM raw_shopify.shopify_orders
  WHERE LOWER(COALESCE(order_test, 'false')) = 'false'
    AND LOWER(order_financial_status) != 'cancelled'
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY
      CASE WHEN order_location_name IS NOT NULL THEN 0 ELSE 1 END,
      date DESC
  ) = 1
)
GROUP BY 1, 2, 3, 4, 5;
