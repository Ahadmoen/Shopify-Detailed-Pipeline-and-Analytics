"""
Shopify Buyer-Seller Distribution Investigation
"""

import requests
import json
import re
from collections import Counter

SHOPIFY_TOKEN = "REPLACE_WITH_SHOPIFY_ACCESS_TOKEN"
SHOP          = "mine-yours-co.myshopify.com"
API_VERSION   = "2024-01"
HEADERS       = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}

def get(url, params=None):
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp

MAX_PAGES = 10

def paginate(url, key, params=None, max_pages=MAX_PAGES):
    results = []
    page = 1
    while url and page <= max_pages:
        r = get(url, params if page == 1 else None)
        data = r.json().get(key, [])
        results.extend(data)
        link = r.headers.get("Link", "")
        nxt  = re.search(r'<([^>]+)>; rel="next"', link)
        url  = nxt.group(1) if nxt else None
        page += 1
        print(f"  page {page-1}: {len(data)} {key} (total: {len(results)})")
    if url:
        print(f"  ... stopped at {max_pages} pages")
    return results

BASE = f"https://{SHOP}/admin/api/{API_VERSION}"

# ─────────────────────────────────────────────────────────────
# CHECK 1a: Smart tag search
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("CHECK 1a: Smart search — seller/consignment tags")
print("="*60)

consignment_customers = []
for search_tag in ["seller", "consign", "consignment", "supplier", "wholesale", "cognito-consignment-update"]:
    r = get(f"{BASE}/customers/search.json", {"query": f"tag:{search_tag}", "limit": 250})
    found = r.json().get("customers", [])
    print(f"\n  tag:{search_tag} → {len(found)} customers")
    for c in found[:5]:
        print(f"    {c.get('first_name','')} {c.get('last_name','')} | tags: {c.get('tags','')} | orders: {c.get('orders_count',0)} | spent: {c.get('total_spent',0)}")
    if search_tag == "cognito-consignment-update":
        consignment_customers = found

# ─────────────────────────────────────────────────────────────
# CHECK 1b: Get ALL cognito-consignment-update customers
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("CHECK 1b: All cognito-consignment-update customers")
print("="*60)

all_consignment = paginate(
    f"{BASE}/customers/search.json",
    "customers",
    {"query": "tag:cognito-consignment-update", "limit": 250},
    max_pages=50
)
print(f"\nTotal consignment sellers found: {len(all_consignment)}")
also_buyers = [c for c in all_consignment if int(c.get("orders_count", 0)) > 0]
print(f"Of those, also have orders (buyers too): {len(also_buyers)}")
print(f"\nTop 10 by total spent:")
sorted_c = sorted(also_buyers, key=lambda x: float(x.get("total_spent", 0)), reverse=True)
for c in sorted_c[:10]:
    print(f"  {c.get('first_name','')} {c.get('last_name','')} | orders: {c.get('orders_count',0)} | spent: ${c.get('total_spent',0)}")

# ─────────────────────────────────────────────────────────────
# CHECK 2: Customer metafields sample
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("CHECK 2: Customer metafields (sample 50)")
print("="*60)

customers_sample = paginate(f"{BASE}/customers.json", "customers", {"limit": 50}, max_pages=1)
meta_namespaces = Counter()
for c in customers_sample:
    r = get(f"{BASE}/customers/{c['id']}/metafields.json")
    mfs = r.json().get("metafields", [])
    for m in mfs:
        key = f"{m.get('namespace')}.{m.get('key')}"
        meta_namespaces[key] += 1

print(f"\nCustomer metafield keys found:")
if meta_namespaces:
    for k, v in meta_namespaces.most_common():
        print(f"  {k}: {v} customers")
else:
    print("  None found")

# ─────────────────────────────────────────────────────────────
# CHECK 3: buy.customer_id lookups
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("CHECK 3: The 3 buy.customer_id customers")
print("="*60)

known_customer_ids = ["6386186518641", "5157593776241", "6049559380081"]
for cid in known_customer_ids:
    try:
        r = get(f"{BASE}/customers/{cid}.json")
        c = r.json().get("customer", {})
        print(f"\n  ID: {cid}")
        print(f"  Name: {c.get('first_name','')} {c.get('last_name','')}")
        print(f"  Email: {c.get('email','')}")
        print(f"  Orders: {c.get('orders_count',0)} | Spent: ${c.get('total_spent',0)}")
        print(f"  Tags: {c.get('tags','')}")
    except Exception as e:
        print(f"  {cid}: ERROR {e}")

# ─────────────────────────────────────────────────────────────
# CHECK 4: Draft orders — are they seller payouts?
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("CHECK 4: Draft orders investigation (18,399 total)")
print("="*60)

r = get(f"{BASE}/draft_orders/count.json")
print(f"Total draft orders: {r.json().get('count', 0)}")

# Get samples by status
for status in ["open", "invoice_sent", "completed"]:
    r = get(f"{BASE}/draft_orders.json", {"limit": 3, "status": status})
    drafts = r.json().get("draft_orders", [])
    print(f"\n--- Status: {status} ({len(drafts)} sample) ---")
    for d in drafts:
        cust = d.get("customer") or {}
        items = d.get("line_items", [])
        print(f"  Draft: {d.get('name')} | Total: {d.get('total_price')} | Tags: {d.get('tags','')}")
        print(f"  Customer: {cust.get('id','')} {cust.get('first_name','')} {cust.get('last_name','')}")
        print(f"  Note: {str(d.get('note',''))[:120]}")
        for item in items[:2]:
            print(f"  Item: {item.get('title','')} | Price: {item.get('price')} | Qty: {item.get('quantity')} | SKU: {item.get('sku','')}")

# Count by status
print(f"\n--- Draft order counts by status ---")
for status in ["open", "invoice_sent", "completed"]:
    r = get(f"{BASE}/draft_orders/count.json", {"status": status})
    print(f"  {status}: {r.json().get('count', 0)}")

# ─────────────────────────────────────────────────────────────
# CHECK 5: Customer notes sample
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("CHECK 5: Customer notes with seller keywords (sample 2,500)")
print("="*60)

customers = paginate(f"{BASE}/customers.json", "customers", {"limit": 250}, max_pages=10)
keywords = ["seller", "consign", "buyout", "sell to us", "supplier", "vendor"]
seller_note_customers = []
for c in customers:
    note = (c.get("note") or "").lower()
    if any(kw in note for kw in keywords):
        seller_note_customers.append({
            "id": c["id"],
            "name": f"{c.get('first_name','')} {c.get('last_name','')}".strip(),
            "note": c.get("note","")[:150]
        })

print(f"\nCustomers with seller notes: {len(seller_note_customers)}")
for c in seller_note_customers[:5]:
    print(f"  {c['name']}: {c['note']}")

# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total consignment-tagged customers:   {len(all_consignment)}")
print(f"Of those, also buyers (have orders):  {len(also_buyers)}")
print(f"buy.customer_id in products:          3 (from BigQuery)")
print(f"Customer metafields with vendor data: {sum(1 for k in meta_namespaces if 'vendor' in k or 'sell' in k)}")
print(f"Draft orders total:                   18,399")
print(f"Seller-related customer notes:        {len(seller_note_customers)}")
