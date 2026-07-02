# BigQuery Reporting Views — final_reporting

All views dedupe raw duplicates internally via `QUALIFY ROW_NUMBER()` (preferring rows with location and customer data), convert dates to **America/Vancouver**, and share a common channel mapping:

```
Point of Sale → Retail
Online Store / Shop → Ecomm
Draft Orders → Draft
3890849 → Gorgias
else → Other
```

| View | Grain | Location | Channel |
|---|---|---|---|
| fact_orders_v2 | Order | ✅ store_location | ✅ |
| fact_daily_sales_v2 | Day × channel × geo × store | ✅ | ✅ |
| fact_product_sales_v2 | Product × day × channel × store | ✅ | ✅ |
| fact_refunds_v2 | Refund line | ✅ (from parent order) | ✅ |
| fact_customers_v2 | Customer | ✅ preferred_store | ✅ preferred_channel |
| fact_inventory_v2 | Product snapshot | ✅ (metafield, JSON-cleaned) | n/a (unsold stock) |
| fact_seller | Seller × contract × store × channel | ✅ | ✅ (of sold items) |
| fact_marketing_v2 | Ad × day | n/a | source (Meta/Google) |
| fact_klaviyo_campaigns_v2 | Campaign | n/a | n/a |

## Reconciliation notes (vs Shopify Admin)
- `net_sales` = `subtotal_price` (after discounts, **before** returns). Shopify Net Sales subtracts returns — expected definitional gap.
- Timezone fix makes daily order counts match Shopify (e.g. Jun 15: 47 vs 45; May: 2,438 vs 2,447 ≈ 0.4%).
- Never compare against Shopify "last non-direct click" attribution reports — they redistribute revenue.
- COGS coverage ≈ 20% of products (client entering costs at intake will improve margin accuracy).
