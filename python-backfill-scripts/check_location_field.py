# ─────────────────────────────────────────────────────────────
# Check Shopify Orders API for location_id field
# Run on Google Colab
# ─────────────────────────────────────────────────────────────

import requests
import json

SHOPIFY_TOKEN = "REPLACE_WITH_SHOPIFY_ACCESS_TOKEN"
SHOP          = "mine-yours-co.myshopify.com"
API_VERSION   = "2024-01"
HEADERS       = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}

# Fetch recent POS orders
url = f"https://{SHOP}/admin/api/{API_VERSION}/orders.json"
params = {"status": "any", "limit": 20}

resp = requests.get(url, headers=HEADERS, params=params)
orders = resp.json().get("orders", [])

print(f"Orders fetched: {len(orders)}\n")

for o in orders:
    if o.get("source_name") == "pos":
        print(f"Order: {o.get('name')}")
        print(f"  location_id: {o.get('location_id')}")
        print(f"  source_name: {o.get('source_name')}")
        print()

# ── Fetch all locations from Shopify ──────────────────────────
print("=" * 60)
print("All Locations in Shopify:")
print("=" * 60)

loc_url = f"https://{SHOP}/admin/api/{API_VERSION}/locations.json"
loc_resp = requests.get(loc_url, headers=HEADERS)
locations = loc_resp.json().get("locations", [])

for loc in locations:
    print(f"ID: {loc.get('id')} | Name: {loc.get('name')} | Address: {loc.get('address1')}, {loc.get('city')}")
