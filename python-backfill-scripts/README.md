# Python Backfill Scripts (Google Colab)

Faster and more reliable than n8n for large historical ranges (35K+ orders in minutes).

| Script | Purpose |
|---|---|
| shopify_orders_backfill.py | Orders with location + customer_id. Append + dedupe pattern (delete blocked by streaming buffer). Logs deleted/inserted counts. |
| shopify_customers_backfill.py | Full customer backfill with tags |
| shopify_products_backfill.py | Products + inventory item costs |
| shopify_product_metafields_backfill.py | buy.* / custom.* metafields |
| meta_ads_backfill.py | Meta Ads via Graph API |
| check_order_cost_field.py | Proved Orders API does NOT return variant_unit_cost |
| check_location_field.py | Verified location_id on orders + fetched all Shopify locations |
| check_customer_id_in_orders.py | Verified customer.id availability in Orders API |
| buyer_seller_investigation.py | Seller↔buyer overlap analysis |

## Critical implementation details
- BigQuery numeric columns are **BIGNUMERIC** — pandas inserts must convert via `Decimal(str(round(x, 4)))` with an explicit schema.
- `date` column must be converted `pd.to_datetime(df["date"]).dt.date` before load.
- Timezone-aware Shopify timestamps must be stripped (`tzinfo=None`) before date math.
- Backfills use `created_at_min/max` to match Shopify Admin counts exactly.

## Post-backfill dedupe (run in BigQuery)
```sql
CREATE OR REPLACE TABLE raw_shopify.shopify_orders_clean AS
SELECT * FROM raw_shopify.shopify_orders
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY order_id, date, line_item__id
  ORDER BY
    CASE WHEN order_location_name IS NOT NULL THEN 0 ELSE 1 END,
    CASE WHEN order_customer_id IS NOT NULL THEN 0 ELSE 1 END,
    date DESC
) = 1;
-- verify count, then:
TRUNCATE TABLE raw_shopify.shopify_orders;
INSERT INTO raw_shopify.shopify_orders SELECT * FROM raw_shopify.shopify_orders_clean;
DROP TABLE raw_shopify.shopify_orders_clean;
```
