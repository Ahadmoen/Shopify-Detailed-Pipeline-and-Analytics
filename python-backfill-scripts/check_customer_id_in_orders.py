# Check if customer_id is available in Shopify Orders API

import requests
import json

SHOPIFY_TOKEN = "REPLACE_WITH_SHOPIFY_ACCESS_TOKEN"
SHOP          = "mine-yours-co.myshopify.com"
API_VERSION   = "2024-01"
HEADERS       = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}

url = f"https://{SHOP}/admin/api/{API_VERSION}/orders.json"
params = {"status": "any", "limit": 3}

resp = requests.get(url, headers=HEADERS, params=params)
orders = resp.json().get("orders", [])

for o in orders:
    print(f"Order: {o.get('name')}")
    print(f"  customer.id:    {o.get('customer', {}).get('id')}")
    print(f"  customer.email: {o.get('customer', {}).get('email')}")
    print(f"  customer keys:  {list(o.get('customer', {}).keys())}")
    print()
