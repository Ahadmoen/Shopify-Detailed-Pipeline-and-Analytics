# ─────────────────────────────────────────────────────────────
# Shopify Products Backfill → BigQuery (with inventory costs)
# Run on Google Colab
# Full backfill — all products
# ─────────────────────────────────────────────────────────────

# !pip install google-cloud-bigquery pandas requests pyarrow -q

import requests
import pandas as pd
import re
from datetime import datetime
from decimal import Decimal
from google.cloud import bigquery
from google.oauth2 import service_account

# ── CONFIG ────────────────────────────────────────────────────
SHOPIFY_TOKEN = "REPLACE_WITH_SHOPIFY_ACCESS_TOKEN"
SHOP          = "mine-yours-co.myshopify.com"
API_VERSION   = "2024-01"
PROJECT       = "mine-and-yours-analytics"
DATASET       = "raw_shopify"
TABLE         = "shopify_products"
START_DATE    = "2020-01-01"   # full history
END_DATE      = datetime.today().strftime('%Y-%m-%d')

# ── CREDENTIALS ───────────────────────────────────────────────
SA_INFO = {
  "type": "service_account",
  "project_id": "REPLACE_WITH_PROJECT_ID",
  "private_key_id": "REPLACE_WITH_PRIVATE_KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQClQXv6WAIgmKF+\nJspq2b6GH4mUYtpKP2fPzr1eMmhAkKATY2Ywy76KeYJqc5fbq7fgIg/54mqzSUok\nbe+U8ihiD/mvzshxLP5lUYjUwE289tK+y8KFxlhHjDyvJ8yEU8gmdIYSvppNXkyZ\nB6FvQ5yos6EHU5Aq71zK/UNkj/4Pxym8gaabP5IbHYjuuflsngJzYvgqvJHoN8sZ\nDHNnq7dUSIm3YnaUVxDsBjcPTRHQ5CeGlYtycjzt+hZz+G2FpGXbieI0RQHM/izt\nOCHcJPJZZM6MSGEcfv0qU3sTn+q1ibtubnV+g5SG4DYOCehzAVQl/iFzHrOZbhpY\nKJRv6PmZAgMBAAECggEAHAb2KuhAPB0GzqlvjR2u5Xp1z/fQA+WrCqCKl24/Jiwh\nKgiirUXw4/Vlu/4s1DHUdqvwP7Y52HxmmbUXfBBx7ue8tieA8UjrQG3KoiKXTKQj\n6/4M2LliAYh0RlSeqBa5jGQY1RcEfniuzwlvRLqX2DjW57Ixcka0Wy0HAAg3057y\nyxGoLlmZxhlyBz2yFWW6IyON/47V82vrjDcjUf4wRKlpiI+kBR2pjxGrJx4ccZ+u\nqCFCPYs9GjE8R95Yhkz6g/3cwrHcWuur0kywBmJtBFW48PdKHw98DoI9t/9F3kzx\nlAnuugiG/XZD/DuAsmrEWjwxeDZ7OSVdkIhxDwtUPQKBgQDXPOw8b+qcA/0wMT/e\nc3Dx9J0iKN3xG1ztLOLY02VdWxbkjuoVGr067DR9S6gDzj6J+t1jM6sVq4XpL1Wa\nf7QItc8NhF+SfVadX1Ro3QFroMtcC/BHY9N/9j6T0XriPPoVHGfR7Up8G+vCsM9S\noeRQe10PvBcMDm8wu1KDiSpFzwKBgQDEjVisemHs6FIGCigaq/oyledp0t2CyJ67\nL+4CAzsg/u+tW6qN0Sz4sQt2K6C8HWg6lPUFp+J6NfCPui021CfCiN+kPPPaBe2+\nuW5j9gfg8VVEMPiEEyX+RksF7nJgn74najKcwCgBUSc5y791RkoGJ2dVvfDL9wxM\n/2+PbXkMFwKBgHGySewHBnxRkx4w9dcRThlRqOuRgOPLG4Rh0JbO3F27L1WetMJf\nNJR6j6OcIm2YNer3LJkpgvdYes1Z5rNNQBHV0EEIqt+b+/P3loQqMoTjFGlUGSHs\n9p1Cu32kC3CU21npfmIjIdR7f0eB1JKG2C83a0pThi0lNtEcMpMvErh7AoGAbrY7\nU3PgAuTdht9jtZpXZPUBE5+d/BPrLP8TbnjJbo2LDbgLerRvQ2neTeLHOA7MbesH\nlPb63+HQLfUtkKux9abJaiaXKKCcSQkEADROPctSPwXiheqPRQntKlske/6eym7M\nMXUfU5aVpL16i6FbAtphH2/M2ea/PAPJoB2GyGMCgYEAu0uo6rULHv8/uOsTwy84\nCL9M+VxblgzNL8fBl0oVqxh7YewEnJGfvCA3PTxFr+qYY1CzHYY8m830RJmleG/M\n1vUyEyiqpgvK4VmFIFYEReSCUhxy9POPsen/QMUfymaGQPaQipBNaHSuE6L7s9Mm\ni5RUrwVUIzTjhbdNYBSrmxo=\n-----END PRIVATE KEY-----\n",
  "client_email": "REPLACE_WITH_CLIENT_EMAIL",
  "client_id": "REPLACE_WITH_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "REPLACE_WITH_CLIENT_X509_CERT_URL",
  "universe_domain": "googleapis.com"
}

credentials = service_account.Credentials.from_service_account_info(SA_INFO)
client = bigquery.Client(project=PROJECT, credentials=credentials)

# ── BIGQUERY SCHEMA ───────────────────────────────────────────
SCHEMA = [
    bigquery.SchemaField("date",                                "DATE"),
    bigquery.SchemaField("product_id",                          "STRING"),
    bigquery.SchemaField("product_title",                       "STRING"),
    bigquery.SchemaField("product_description",                 "STRING"),
    bigquery.SchemaField("product_handle",                      "STRING"),
    bigquery.SchemaField("product_image_src",                   "STRING"),
    bigquery.SchemaField("product_inventory_quantity",          "BIGNUMERIC"),
    bigquery.SchemaField("product_price",                       "BIGNUMERIC"),
    bigquery.SchemaField("product_status",                      "STRING"),
    bigquery.SchemaField("product_tags",                        "STRING"),
    bigquery.SchemaField("product_type",                        "STRING"),
    bigquery.SchemaField("product_created_at_datetime",         "STRING"),
    bigquery.SchemaField("product_updated_at_datetime",         "STRING"),
    bigquery.SchemaField("product_variant_inventory_item_cost", "BIGNUMERIC"),
    bigquery.SchemaField("product_vendor",                      "STRING"),
]

HEADERS = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}

# ── FETCH ALL PRODUCTS ────────────────────────────────────────
def fetch_all_products():
    url    = f"https://{SHOP}/admin/api/{API_VERSION}/products.json"
    params = {"created_at_min": START_DATE, "created_at_max": END_DATE, "limit": 250}
    all_products = []
    page = 1
    while url:
        print(f"  Fetching page {page}...", end=" ")
        resp = requests.get(url, headers=HEADERS, params=params if page == 1 else None)
        if resp.status_code != 200:
            print(f"ERROR {resp.status_code}: {resp.text}")
            break
        products = resp.json().get("products", [])
        all_products.extend(products)
        print(f"{len(products)} products (total: {len(all_products)})")
        link       = resp.headers.get("Link", "")
        next_match = re.search(r'<([^>]+)>; rel="next"', link)
        url        = next_match.group(1) if next_match else None
        page      += 1
    return all_products

# ── FETCH INVENTORY ITEM COSTS (batches of 250) ───────────────
def fetch_inventory_costs(products):
    # Extract all inventory_item_ids
    ids = []
    for p in products:
        for v in p.get("variants", []):
            iid = v.get("inventory_item_id")
            if iid:
                ids.append(str(iid))

    cost_map = {}
    total_batches = (len(ids) + 249) // 250
    print(f"\nFetching costs for {len(ids)} inventory items in {total_batches} batches...")

    for i in range(0, len(ids), 250):
        batch      = ids[i:i + 250]
        batch_num  = i // 250 + 1
        url        = f"https://{SHOP}/admin/api/{API_VERSION}/inventory_items.json"
        params     = {"ids": ",".join(batch)}
        print(f"  Batch {batch_num}/{total_batches}...", end=" ")
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code != 200:
            print(f"ERROR {resp.status_code}: {resp.text}")
            continue
        items = resp.json().get("inventory_items", [])
        for item in items:
            iid  = str(item.get("id", ""))
            cost = item.get("cost")
            cost_map[iid] = float(cost) if cost is not None else None
        print(f"{len(items)} items fetched ({len(cost_map)} costs so far)")

    has_cost = sum(1 for v in cost_map.values() if v is not None)
    print(f"\n✅ Cost map built — {has_cost}/{len(cost_map)} items have cost")
    return cost_map

# ── TRANSFORM ─────────────────────────────────────────────────
def transform_products(products, cost_map):
    today = datetime.today().strftime('%Y-%m-%d')
    rows  = []
    for p in products:
        variants = p.get("variants", [])
        fv       = variants[0] if variants else {}
        qty      = sum(int(v.get("inventory_quantity") or 0) for v in variants)
        images   = p.get("images", [])
        iid      = str(fv.get("inventory_item_id", ""))
        cost     = cost_map.get(iid)  # None if not found or not entered in Shopify
        rows.append({
            "date":                                today,
            "product_id":                          str(p.get("id", "")),
            "product_title":                       p.get("title", ""),
            "product_description":                 p.get("body_html", "") or "",
            "product_handle":                      p.get("handle", ""),
            "product_image_src":                   images[0]["src"] if images else "",
            "product_inventory_quantity":          qty,
            "product_price":                       float(fv.get("price") or 0),
            "product_status":                      (p.get("status") or "").upper(),
            "product_tags":                        p.get("tags", ""),
            "product_type":                        p.get("product_type", ""),
            "product_created_at_datetime":         p.get("created_at"),
            "product_updated_at_datetime":         p.get("updated_at"),
            "product_variant_inventory_item_cost": cost,
            "product_vendor":                      p.get("vendor", "")
        })
    return rows

# ── INSERT TO BIGQUERY ────────────────────────────────────────
def insert_to_bigquery(rows):
    if not rows:
        print("No rows to insert.")
        return

    df = pd.DataFrame(rows)

    str_cols = [
        "product_id", "product_title", "product_description", "product_handle",
        "product_image_src", "product_status", "product_tags",
        "product_type", "product_vendor",
    ]
    for col in str_cols:
        df[col] = df[col].fillna("").astype(str)

    df["date"] = pd.to_datetime(df["date"]).dt.date

    df["product_inventory_quantity"] = (
        pd.to_numeric(df["product_inventory_quantity"], errors="coerce")
        .fillna(0)
        .apply(lambda x: Decimal(str(int(x))))
    )
    df["product_price"] = (
        pd.to_numeric(df["product_price"], errors="coerce")
        .fillna(0)
        .apply(lambda x: Decimal(str(round(x, 2))))
    )
    df["product_variant_inventory_item_cost"] = (
        pd.to_numeric(df["product_variant_inventory_item_cost"], errors="coerce")
        .apply(lambda x: Decimal(str(round(x, 2))) if pd.notna(x) else None)
    )
    df["product_created_at_datetime"] = df["product_created_at_datetime"].fillna("").astype(str)
    df["product_updated_at_datetime"] = df["product_updated_at_datetime"].fillna("").astype(str)

    table_ref  = f"{PROJECT}.{DATASET}.{TABLE}"
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # clean replace — table was already truncated
        schema=SCHEMA,
    )
    print(f"\nInserting {len(df)} rows into {table_ref}...")
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"✅ Done — {len(df)} rows inserted into {TABLE}")

# ── RUN ───────────────────────────────────────────────────────
print("=" * 60)
print(f"Shopify Products Backfill: {START_DATE} → {END_DATE}")
print("=" * 60)

print("\n[1/3] Fetching all products...")
products = fetch_all_products()
print(f"Total products fetched: {len(products)}")

print("\n[2/3] Fetching inventory item costs...")
cost_map = fetch_inventory_costs(products)

print("\n[3/3] Transforming + inserting to BigQuery...")
rows = transform_products(products, cost_map)
insert_to_bigquery(rows)

print("\n✅ Backfill complete!")
