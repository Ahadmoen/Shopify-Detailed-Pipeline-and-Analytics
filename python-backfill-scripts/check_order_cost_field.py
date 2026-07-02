# ─────────────────────────────────────────────────────────────
# Check if Shopify Orders API returns line_item variant cost
# Run on Google Colab
# ─────────────────────────────────────────────────────────────

import requests
import json

SHOPIFY_TOKEN = "REPLACE_WITH_SHOPIFY_ACCESS_TOKEN"
SHOP          = "mine-yours-co.myshopify.com"
API_VERSION   = "2024-01"
HEADERS       = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}

# Fetch last 10 orders
url = f"https://{SHOP}/admin/api/{API_VERSION}/orders.json"
params = {"status": "any", "limit": 10}

resp = requests.get(url, headers=HEADERS, params=params)
orders = resp.json().get("orders", [])

print(f"Orders fetched: {len(orders)}")
print("=" * 60)

has_cost = 0
no_cost  = 0

for o in orders:
    print(f"\nOrder: {o.get('name')} | Source: {o.get('source_name')}")
    for li in (o.get("line_items") or []):
        cost = li.get("variant_unit_cost") or li.get("cost") or None
        # Also check price_set and total_discount
        print(f"  Item: {li.get('title', '')[:40]}")
        print(f"    price:              {li.get('price')}")
        print(f"    variant_unit_cost:  {cost}")
        print(f"    All keys:           {list(li.keys())}")
        if cost:
            has_cost += 1
        else:
            no_cost += 1

print("\n" + "=" * 60)
print(f"Line items with cost:    {has_cost}")
print(f"Line items without cost: {no_cost}")
print("\nConclusion: Cost field available in Orders API?", "YES" if has_cost > 0 else "NO")
