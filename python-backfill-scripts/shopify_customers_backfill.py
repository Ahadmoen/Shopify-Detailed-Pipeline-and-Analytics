# ─────────────────────────────────────────────────────────────
# Shopify Customers Backfill → BigQuery (with tags)
# Run on Google Colab
# Date range: 2026-01-01 to today
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
TABLE         = "shopify_customers"
START_DATE    = "2026-01-01"
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

# ── SCHEMA — matches BQ table exactly (all numeric = BIGNUMERIC) ──
SCHEMA = [
    bigquery.SchemaField("date",                                 "DATE"),
    bigquery.SchemaField("customer_id",                          "STRING"),
    bigquery.SchemaField("customer_first_name",                  "STRING"),
    bigquery.SchemaField("customer_last_name",                   "STRING"),
    bigquery.SchemaField("customer_created_at",                  "STRING"),
    bigquery.SchemaField("customer_updated_at",                  "STRING"),
    bigquery.SchemaField("customer_currency",                    "STRING"),
    bigquery.SchemaField("customer_default_address_city",        "STRING"),
    bigquery.SchemaField("customer_default_address_country",     "STRING"),
    bigquery.SchemaField("customer_default_address_country_code","STRING"),
    bigquery.SchemaField("customer_orders_count",                "BIGNUMERIC"),
    bigquery.SchemaField("customer_total_spent",                 "BIGNUMERIC"),
    bigquery.SchemaField("customer_aov",                         "BIGNUMERIC"),
    bigquery.SchemaField("customer_is_returning",                "STRING"),
    bigquery.SchemaField("customer_tags",                        "STRING"),
]

HEADERS   = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}
table_ref = f"{PROJECT}.{DATASET}.{TABLE}"

# ── STEP 1: TRUNCATE ──────────────────────────────────────────
print("=" * 60)
print("STEP 1: Truncating shopify_customers in BigQuery...")
client.query(f"TRUNCATE TABLE `{table_ref}`").result()
print("✅ Table truncated")

# ── STEP 2: FETCH CUSTOMERS ───────────────────────────────────
print(f"\n{'='*60}")
print(f"STEP 2: Fetching customers created {START_DATE} → {END_DATE}...")
print("=" * 60)

url    = f"https://{SHOP}/admin/api/{API_VERSION}/customers.json"
params = {
    "created_at_min": START_DATE,
    "created_at_max": END_DATE,
    "limit": 250
}
all_customers = []
page = 1

while url:
    print(f"  Page {page}...", end=" ")
    resp = requests.get(url, headers=HEADERS, params=params if page == 1 else None)
    if resp.status_code != 200:
        print(f"ERROR {resp.status_code}: {resp.text}")
        break
    customers = resp.json().get("customers", [])
    if not customers:
        print("done")
        break
    all_customers.extend(customers)
    print(f"{len(customers)} (total: {len(all_customers)})")
    link       = resp.headers.get("Link", "")
    next_match = re.search(r'<([^>]+)>; rel="next"', link)
    url        = next_match.group(1) if next_match else None
    page      += 1

print(f"\nTotal customers fetched: {len(all_customers)}")

# ── STEP 3: TRANSFORM ─────────────────────────────────────────
print(f"\n{'='*60}")
print("STEP 3: Transforming...")
print("=" * 60)

today = datetime.today().strftime('%Y-%m-%d')
rows  = []

for c in all_customers:
    orders_count = int(c.get("orders_count") or 0)
    total_spent  = float(c.get("total_spent") or 0)
    addr         = c.get("default_address") or {}
    aov          = round(total_spent / orders_count, 2) if orders_count > 0 else 0.0
    rows.append({
        "date":                                  today,
        "customer_id":                           str(c.get("id", "")),
        "customer_first_name":                   c.get("first_name") or "",
        "customer_last_name":                    c.get("last_name") or "",
        "customer_created_at":                   c.get("created_at") or "",
        "customer_updated_at":                   c.get("updated_at") or "",
        "customer_currency":                     c.get("currency") or "",
        "customer_default_address_city":         addr.get("city") or "",
        "customer_default_address_country":      addr.get("country") or "",
        "customer_default_address_country_code": addr.get("country_code") or "",
        "customer_orders_count":                 orders_count,
        "customer_total_spent":                  total_spent,
        "customer_aov":                          aov,
        "customer_is_returning":                 "True" if orders_count > 1 else "False",
        "customer_tags":                         c.get("tags") or "",
    })

consignment = sum(1 for r in rows if "cognito-consignment" in r["customer_tags"].lower())
print(f"Rows prepared:           {len(rows)}")
print(f"Consignment sellers:     {consignment}")

# ── STEP 4: INSERT (batches of 5,000) ────────────────────────
print(f"\n{'='*60}")
print("STEP 4: Inserting to BigQuery...")
print("=" * 60)

BATCH_SIZE    = 5000
total_batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
total_inserted = 0

for i in range(0, len(rows), BATCH_SIZE):
    batch = rows[i:i + BATCH_SIZE]
    df    = pd.DataFrame(batch)

    # String columns
    str_cols = [
        "customer_id", "customer_first_name", "customer_last_name",
        "customer_currency", "customer_default_address_city",
        "customer_default_address_country", "customer_default_address_country_code",
        "customer_is_returning", "customer_tags",
        "customer_created_at", "customer_updated_at"
    ]
    for col in str_cols:
        df[col] = df[col].fillna("").astype(str)

    df["date"] = pd.to_datetime(df["date"]).dt.date

    # BIGNUMERIC — must use Decimal
    df["customer_orders_count"] = (
        pd.to_numeric(df["customer_orders_count"], errors="coerce")
        .fillna(0).apply(lambda x: Decimal(str(int(x))))
    )
    df["customer_total_spent"] = (
        pd.to_numeric(df["customer_total_spent"], errors="coerce")
        .fillna(0).apply(lambda x: Decimal(str(round(x, 2))))
    )
    df["customer_aov"] = (
        pd.to_numeric(df["customer_aov"], errors="coerce")
        .fillna(0).apply(lambda x: Decimal(str(round(x, 2))))
    )

    batch_num = i // BATCH_SIZE + 1
    print(f"  Batch {batch_num}/{total_batches} ({len(df)} rows)...", end=" ")

    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND", schema=SCHEMA)
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    total_inserted += len(df)
    print("✅")

print(f"\n✅ {total_inserted} rows inserted")

# ── STEP 5: VERIFY ────────────────────────────────────────────
print(f"\n{'='*60}")
print("STEP 5: Verification")
print("=" * 60)

result = client.query(f"""
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT customer_id) AS unique_customers,
  COUNTIF(customer_tags IS NOT NULL AND customer_tags != '') AS has_tags,
  COUNTIF(LOWER(customer_tags) LIKE '%cognito-consignment%') AS consignment_sellers,
  COUNTIF(customer_orders_count > 0
    AND LOWER(customer_tags) LIKE '%cognito-consignment%') AS seller_also_buyer
FROM `{table_ref}`
""").result()

for row in result:
    print(f"Total rows:           {row.total_rows}")
    print(f"Unique customers:     {row.unique_customers}")
    print(f"Has tags:             {row.has_tags}")
    print(f"Consignment sellers:  {row.consignment_sellers}")
    print(f"Seller + buyer:       {row.seller_also_buyer}")
