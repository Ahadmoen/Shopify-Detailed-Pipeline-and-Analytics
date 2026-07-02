# n8n Pipelines

Daily automated pipelines running on Railway at **1PM** with a **2-day lookback** (`updated_at_min = today - 2 days`) to catch same-day orders. Each workflow also contains a manual-trigger **backfill branch** using `created_at_min/max` (never `updated_at` — that over-fetches orders touched but not created in the window).

| Workflow | Table | Notes |
|---|---|---|
| shopify_orders_pipeline.json | raw_shopify.shopify_orders | Includes location_id→store name map, customer_id |
| shopify_customers_pipeline.json | raw_shopify.shopify_customers | Tags used for consignment seller identification |
| shopify_products_pipeline.json | raw_shopify.shopify_products | Second call to inventory_items for unit cost |
| shopify_product_metafields_pipeline.json | raw_shopify.shopify_product_metafields | buy.* and custom.* namespaces |
| shopify_refunds_pipeline.json | raw_shopify.shopify_refunds | Line-item refund detail |
| klaviyo_pipeline.json | raw_marketing.klaviyo_* | Pulls last 30 days each run — self-healing |
| meta_ads_pipeline.json | raw_marketing.meta_ads | Facebook Graph API — awaiting valid client account |
| google-ads-appscript/ | raw_marketing.google_ads | Apps Script via Windsor (temporary until Standard access) |

## Known n8n gotchas fixed in these workflows
- Never prefix date values with `=` in query parameters — Shopify silently ignores the filter.
- "Malicious string" validation error on dynamic URLs — split URL and pass ids via query parameters instead of string concatenation.
- BigQuery insert node uses streaming inserts — rows are locked from DELETE for ~30-90 min (streaming buffer).
