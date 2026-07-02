# ─────────────────────────────────────────────────────────────
# Shopify Product Metafields Backfill → BigQuery
# Run on Google Colab
# Date range: 2026-03-01 to 2026-06-10
# ─────────────────────────────────────────────────────────────

# !pip install google-cloud-bigquery pandas requests pyarrow -q

import requests
import pandas as pd
import re
import time
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account

# ── CONFIG ────────────────────────────────────────────────────
SHOPIFY_TOKEN = "REPLACE_WITH_SHOPIFY_ACCESS_TOKEN"
SHOP          = "mine-yours-co.myshopify.com"
API_VERSION   = "2024-01"
PROJECT       = "mine-and-yours-analytics"
DATASET       = "raw_shopify"
TABLE         = "shopify_product_metafields"
START_DATE    = "2026-03-01"
END_DATE      = "2026-06-10"
BATCH_SIZE    = 500

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
HEADERS = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}

# ── FETCH ALL PRODUCTS ────────────────────────────────────────
def fetch_all_products():
    url = f"https://{SHOP}/admin/api/{API_VERSION}/products.json"
    params = {"created_at_min": START_DATE, "created_at_max": END_DATE, "fields": "id,title"}
    all_products = []
    page = 1
    while url:
        print(f"  Fetching products page {page}...", end=" ")
        resp = requests.get(url, headers=HEADERS, params=params if page == 1 else None)
        if resp.status_code != 200:
            print(f"ERROR {resp.status_code}: {resp.text}")
            break
        products = resp.json().get("products", [])
        all_products.extend(products)
        print(f"{len(products)} (total: {len(all_products)})")
        link = resp.headers.get("Link", "")
        next_match = re.search(r'<([^>]+)>; rel="next"', link)
        url = next_match.group(1) if next_match else None
        page += 1
    return all_products

# ── FETCH METAFIELDS FOR ONE PRODUCT ─────────────────────────
def fetch_metafields(product_id):
    url = f"https://{SHOP}/admin/api/{API_VERSION}/products/{product_id}/metafields.json"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        return resp.json().get("metafields", [])
    return []

# ── INSERT BATCH TO BIGQUERY ──────────────────────────────────
def insert_batch(rows, batch_num):
    if not rows:
        return
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    table_ref = f"{PROJECT}.{DATASET}.{TABLE}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"  ✅ Batch {batch_num} inserted — {len(rows)} rows")

# ── RUN ───────────────────────────────────────────────────────
print("=" * 55)
print("Shopify Product Metafields Backfill: Mar 1 → Jun 10")
print("=" * 55)

today = datetime.today().strftime('%Y-%m-%d')
products = fetch_all_products()
print(f"\nTotal products to process: {len(products)}")
print("Now fetching metafields for each product...\n")

all_rows = []
batch_num = 1
total_inserted = 0

for idx, p in enumerate(products):
    product_id    = str(p.get("id", ""))
    product_title = p.get("title", "")
    metafields    = fetch_metafields(product_id)

    for m in metafields:
        all_rows.append({
            "date":                        today,
            "product_id":                  product_id,
            "product_title":               product_title,
            "product_metafield_key":       m.get("key", ""),
            "product_metafield_namespace": m.get("namespace", ""),
            "product_metafield_type":      m.get("type", ""),
            "product_metafield_update_at": m.get("updated_at"),
            "product_metafield_value":     str(m["value"]) if m.get("value") is not None else None
        })

    if (idx + 1) % 50 == 0:
        print(f"  Processed {idx + 1}/{len(products)} products — {len(all_rows)} metafields collected")

    if len(all_rows) >= BATCH_SIZE:
        insert_batch(all_rows, batch_num)
        total_inserted += len(all_rows)
        all_rows = []
        batch_num += 1
        time.sleep(0.5)

if all_rows:
    insert_batch(all_rows, batch_num)
    total_inserted += len(all_rows)

print(f"\n✅ All done — {total_inserted} total metafield rows inserted into {TABLE}")
