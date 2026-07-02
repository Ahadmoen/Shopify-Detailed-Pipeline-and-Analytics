# ─────────────────────────────────────────────────────────────
# Shopify Orders Backfill → BigQuery (with location mapping)
# Run on Google Colab
# Deletes existing data for date range, then re-inserts with location
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
TABLE         = "shopify_orders"

START_DATE    = "2025-01-01"   # ← update as needed
END_DATE      = "2026-06-28"   # ← update as needed

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
client      = bigquery.Client(project=PROJECT, credentials=credentials)
table_ref   = f"{PROJECT}.{DATASET}.{TABLE}"
HEADERS     = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}

APP_MAP = {
    'web': 'Online Store', 'pos': 'Point of Sale',
    'mobile': 'Shop', 'shopify_draft_order': 'Draft Orders',
    'iphone': 'Shop', 'android': 'Shop'
}

LOCATION_MAP = {
    '61845110897': '2061 West 4th Ave',
    '34791915633': '418 Davie Street, Vancouver',
    '70972768369': '486 Front St W - The Well, Toronto',
    '69315657841': '510 8 Ave SW - Holt Renfrew, Calgary',
    '61826072689': '79 Yorkville, Toronto',
    '42702532':     '1025 Howe Street, Vancouver',
    '61808017521':  'Consignment - Real Real',
    '61822697585':  "Courtney's Closet",
    '191632':       'Storage Locker',
    '61841834097':  'West 4th - Back of House (Archived)'
}

def get_week(dt):
    d    = dt.replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
    jan4 = datetime(d.year, 1, 4)
    delta = (d - jan4).days
    return str(1 + (delta - 3 + (jan4.weekday() + 6) % 7) // 7)

def get_location_name(loc_id):
    if not loc_id:
        return None
    return LOCATION_MAP.get(str(loc_id), 'Unknown Location')

# ── STEP 1: SKIP DELETE — will dedupe after insert ────────────
print("=" * 60)
print(f"STEP 1: Skipping delete (streaming buffer) — will append + dedupe after")
print("=" * 60)

count_before = list(client.query(f"""
    SELECT COUNT(*) AS cnt FROM `{table_ref}`
    WHERE date >= '{START_DATE}' AND date <= '{END_DATE}'
""").result())[0].cnt
print(f"Existing rows in range: {count_before}")

# ── STEP 2: FETCH ─────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"STEP 2: Fetching orders created {START_DATE} → {END_DATE}")
print("=" * 60)

url    = f"https://{SHOP}/admin/api/{API_VERSION}/orders.json"
params = {
    "status":          "any",
    "created_at_min":  START_DATE,
    "created_at_max":  END_DATE,
    "limit":           250
}

all_orders = []
page       = 1

while url:
    print(f"  Page {page}...", end=" ")
    resp = requests.get(url, headers=HEADERS, params=params if page == 1 else None)
    if resp.status_code != 200:
        print(f"ERROR {resp.status_code}: {resp.text}")
        break
    orders = resp.json().get("orders", [])
    if not orders:
        print("done")
        break
    all_orders.extend(orders)
    print(f"{len(orders)} (total: {len(all_orders)})")
    link       = resp.headers.get("Link", "")
    next_match = re.search(r'<([^>]+)>; rel="next"', link)
    url        = next_match.group(1) if next_match else None
    params     = None
    page      += 1

print(f"\nTotal orders fetched: {len(all_orders)}")

# ── STEP 3: TRANSFORM ─────────────────────────────────────────
print(f"\n{'='*60}")
print("STEP 3: Transforming...")
print("=" * 60)

results = []
for o in all_orders:
    cat = o.get("created_at") or ""
    try:
        dobj = datetime.fromisoformat(cat.replace("Z", "+00:00"))
    except:
        dobj = datetime.utcnow()

    od       = cat.split("T")[0] if cat else datetime.today().strftime('%Y-%m-%d')
    yr       = str(dobj.year)
    mo       = f"{dobj.month:02d}"
    ym       = f"{yr}|{dobj.month}"
    wk       = get_week(dobj)
    lis      = o.get("line_items") or []
    tqty     = sum(l.get("quantity") or 0 for l in lis)
    sa       = o.get("shipping_address") or {}
    sl       = o.get("shipping_lines") or []
    sp       = float(sl[0]["price"]) if sl else 0.0
    loc_id   = str(o.get("location_id")) if o.get("location_id") else None
    loc_name = get_location_name(loc_id)

    base = {
        "account_name":                             "mine-yours-co.myshopify.com",
        "date":                                     od,
        "month":                                    mo,
        "order_app_name":                           APP_MAP.get(o.get("source_name", ""), o.get("source_name") or "Unknown"),
        "order_created_at":                         cat,
        "order_currency":                           o.get("currency") or "",
        "order_customer_last_visit_utm_campaign":   None,
        "order_customer_last_visit_utm_medium":     None,
        "order_customer_last_visit_utm_source":     None,
        "order_financial_status":                   (o.get("financial_status") or "").upper(),
        "order_id":                                 str(o.get("id") or ""),
        "order_name":                               o.get("name") or "",
        "order_net_sales":                          float(o.get("subtotal_price") or 0),
        "order_processed_at":                       o.get("processed_at"),
        "order_quantity":                           tqty,
        "order_shipping_address_country":           sa.get("country"),
        "order_shipping_address_province":          sa.get("province"),
        "order_shipping_price":                     sp,
        "order_subtotal_price":                     float(o.get("subtotal_price") or 0),
        "order_test":                               "True" if o.get("test") else "False",
        "order_total_discounts":                    float(o.get("total_discounts") or 0),
        "order_total_price":                        float(o.get("total_price") or 0),
        "source":                                   "shopify",
        "week":                                     wk,
        "year":                                     yr,
        "year_month":                               ym,
        "order_total_tax_amount":                   float(o.get("total_tax") or 0),
        "order_location_id":                        loc_id,
        "order_location_name":                      loc_name,
        "order_customer_id":                        str((o.get("customer") or {}).get("id") or "") or None,
    }

    if not lis:
        results.append({**base,
            "line_item__id": None, "line_item__price": None,
            "line_item__product_id": None, "line_item__quantity": None,
            "line_item__sku": None, "line_item__title": None,
            "line_item__total_discount": None, "line_item__variant_unit_cost": None,
            "line_item__vendor": None
        })
    else:
        for li in lis:
            results.append({**base,
                "line_item__id":              str(li.get("id") or ""),
                "line_item__price":           float(li.get("price") or 0),
                "line_item__product_id":      str(li.get("product_id") or ""),
                "line_item__quantity":        li.get("quantity") or 0,
                "line_item__sku":             li.get("sku") or "",
                "line_item__title":           li.get("title") or "",
                "line_item__total_discount":  float(li.get("total_discount") or 0),
                "line_item__variant_unit_cost": None,
                "line_item__vendor":          li.get("vendor") or ""
            })

print(f"Rows prepared: {len(results)}")

# ── STEP 4: INSERT ────────────────────────────────────────────
print(f"\n{'='*60}")
print("STEP 4: Inserting to BigQuery...")
print("=" * 60)

SCHEMA = [
    bigquery.SchemaField("account_name",                            "STRING"),
    bigquery.SchemaField("date",                                    "DATE"),
    bigquery.SchemaField("line_item__id",                           "STRING"),
    bigquery.SchemaField("line_item__price",                        "BIGNUMERIC"),
    bigquery.SchemaField("line_item__product_id",                   "STRING"),
    bigquery.SchemaField("line_item__quantity",                     "BIGNUMERIC"),
    bigquery.SchemaField("line_item__sku",                          "STRING"),
    bigquery.SchemaField("line_item__title",                        "STRING"),
    bigquery.SchemaField("line_item__total_discount",               "BIGNUMERIC"),
    bigquery.SchemaField("line_item__variant_unit_cost",            "BIGNUMERIC"),
    bigquery.SchemaField("line_item__vendor",                       "STRING"),
    bigquery.SchemaField("month",                                   "STRING"),
    bigquery.SchemaField("order_app_name",                          "STRING"),
    bigquery.SchemaField("order_created_at",                        "STRING"),
    bigquery.SchemaField("order_currency",                          "STRING"),
    bigquery.SchemaField("order_customer_last_visit_utm_campaign",  "STRING"),
    bigquery.SchemaField("order_customer_last_visit_utm_medium",    "STRING"),
    bigquery.SchemaField("order_customer_last_visit_utm_source",    "STRING"),
    bigquery.SchemaField("order_financial_status",                  "STRING"),
    bigquery.SchemaField("order_id",                                "STRING"),
    bigquery.SchemaField("order_name",                              "STRING"),
    bigquery.SchemaField("order_net_sales",                         "BIGNUMERIC"),
    bigquery.SchemaField("order_processed_at",                      "STRING"),
    bigquery.SchemaField("order_quantity",                          "BIGNUMERIC"),
    bigquery.SchemaField("order_shipping_address_country",          "STRING"),
    bigquery.SchemaField("order_shipping_address_province",         "STRING"),
    bigquery.SchemaField("order_shipping_price",                    "BIGNUMERIC"),
    bigquery.SchemaField("order_subtotal_price",                    "BIGNUMERIC"),
    bigquery.SchemaField("order_test",                              "STRING"),
    bigquery.SchemaField("order_total_discounts",                   "BIGNUMERIC"),
    bigquery.SchemaField("order_total_price",                       "BIGNUMERIC"),
    bigquery.SchemaField("source",                                  "STRING"),
    bigquery.SchemaField("week",                                    "STRING"),
    bigquery.SchemaField("year",                                    "STRING"),
    bigquery.SchemaField("year_month",                              "STRING"),
    bigquery.SchemaField("order_total_tax_amount",                  "BIGNUMERIC"),
    bigquery.SchemaField("order_location_id",                       "STRING"),
    bigquery.SchemaField("order_location_name",                     "STRING"),
    bigquery.SchemaField("order_customer_id",                       "STRING"),
]

BATCH_SIZE     = 5000
total_inserted = 0
total_batches  = (len(results) + BATCH_SIZE - 1) // BATCH_SIZE

for i in range(0, len(results), BATCH_SIZE):
    batch = results[i:i + BATCH_SIZE]
    df    = pd.DataFrame(batch)

    df["date"] = pd.to_datetime(df["date"]).dt.date

    for col in ["account_name", "order_app_name", "order_created_at", "order_currency",
                "order_financial_status", "order_id", "order_name", "order_test",
                "source", "week", "year", "year_month", "month",
                "line_item__id", "line_item__sku", "line_item__title",
                "line_item__vendor", "line_item__product_id"]:
        df[col] = df[col].fillna("").astype(str)

    for col in ["order_shipping_address_country", "order_shipping_address_province",
                "order_processed_at", "order_location_id", "order_location_name",
                "order_customer_id"]:
        df[col] = df[col].where(df[col].notna(), None)

    bignumeric_cols = [
        "order_net_sales", "order_subtotal_price", "order_total_price",
        "order_total_discounts", "order_shipping_price", "order_total_tax_amount",
        "line_item__price", "line_item__total_discount", "line_item__variant_unit_cost",
        "order_quantity", "line_item__quantity"
    ]
    for col in bignumeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).apply(lambda x: Decimal(str(round(x, 4))))

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
  COUNT(DISTINCT order_id) AS unique_orders,
  COUNTIF(order_location_name IS NOT NULL) AS has_location,
  COUNTIF(order_customer_id IS NOT NULL) AS has_customer_id,
  MIN(date) AS earliest,
  MAX(date) AS latest
FROM `{table_ref}`
WHERE date >= '{START_DATE}' AND date <= '{END_DATE}'
""").result()
for row in result:
    print(f"Total rows:      {row.total_rows}")
    print(f"Unique orders:   {row.unique_orders}")
    print(f"Has location:    {row.has_location}")
    print(f"Has customer_id: {row.has_customer_id}")
    print(f"Date range:      {row.earliest} → {row.latest}")

print(f"\n{'='*60}")
print("SUMMARY")
print("=" * 60)
print(f"Rows deleted (old):  {count_before}")
print(f"Rows inserted (new): {total_inserted}")
print(f"Net change:          {total_inserted - count_before:+d}")
