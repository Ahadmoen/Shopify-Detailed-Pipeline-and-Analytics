# ─────────────────────────────────────────────────────────────
# Meta Ads Backfill → BigQuery
# Run on Google Colab
# ─────────────────────────────────────────────────────────────

# !pip install google-cloud-bigquery pandas requests pyarrow -q

import requests
import pandas as pd
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.oauth2 import service_account

# ── CONFIG ────────────────────────────────────────────────────
ACCESS_TOKEN  = "EAAObRv5d7ekBRtBTMlSI0ADIxs9wfZA3mAcDpkB4opB1ZBRFsQ2eaLDPquKAYkquVGQp3jojXEsyk6PojkkK00W2qgjzAoPqAUqI7VaFCrmzfnX7vAPyIpHMBhYFssuVTB8UgQvGqyvgXP3xuwS9lQau3g0ks97OaOSNtiZCUtirDgjDEai7rcoWiTHC8ZAIEBz46nWiRAZDZD"
AD_ACCOUNT_ID = "act_2626840940790152"
API_VERSION   = "v23.0"
PROJECT       = "mine-and-yours-analytics"
DATASET       = "raw_marketing"
TABLE         = "meta_ads"

# ── DATE RANGE — update as needed ────────────────────────────
START_DATE    = "2026-01-01"
END_DATE      = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

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
table_ref = f"{PROJECT}.{DATASET}.{TABLE}"

# ── SCHEMA ────────────────────────────────────────────────────
SCHEMA = [
    bigquery.SchemaField("date",              "DATE"),
    bigquery.SchemaField("campaign_id",       "STRING"),
    bigquery.SchemaField("campaign_name",     "STRING"),
    bigquery.SchemaField("adset_id",          "STRING"),
    bigquery.SchemaField("adset_name",        "STRING"),
    bigquery.SchemaField("ad_id",             "STRING"),
    bigquery.SchemaField("ad_name",           "STRING"),
    bigquery.SchemaField("spend",             "FLOAT64"),
    bigquery.SchemaField("impressions",       "INT64"),
    bigquery.SchemaField("clicks",            "INT64"),
    bigquery.SchemaField("reach",             "INT64"),
    bigquery.SchemaField("purchases",         "INT64"),
    bigquery.SchemaField("purchase_value",    "FLOAT64"),
    bigquery.SchemaField("purchase_roas",     "FLOAT64"),
    bigquery.SchemaField("account_currency",  "STRING"),
    bigquery.SchemaField("synced_at",         "TIMESTAMP"),
]

# ── FETCH META ADS DATA ───────────────────────────────────────
def fetch_meta_ads(start_date, end_date):
    url = f"https://graph.facebook.com/{API_VERSION}/{AD_ACCOUNT_ID}/insights"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "ad_id,ad_name,campaign_id,campaign_name,adset_id,adset_name,spend,impressions,clicks,reach,actions,action_values,account_currency",
        "time_range": f'{{"since":"{start_date}","until":"{end_date}"}}',
        "level": "ad",
        "limit": 500
    }
    all_data = []
    page = 1
    while url:
        print(f"  Page {page}...", end=" ")
        resp = requests.get(url, params=params if page == 1 else None)
        if resp.status_code != 200:
            print(f"ERROR {resp.status_code}: {resp.text}")
            break
        data = resp.json()
        rows = data.get("data", [])
        all_data.extend(rows)
        print(f"{len(rows)} rows (total: {len(all_data)})")
        next_url = data.get("paging", {}).get("next")
        url = next_url
        params = None
        page += 1
    return all_data

# ── TRANSFORM ─────────────────────────────────────────────────
def transform(data):
    synced_at = datetime.utcnow().isoformat()
    rows = []
    for d in data:
        purchase_action = next((a for a in (d.get("actions") or []) if a["action_type"] == "purchase"), None)
        purchases = int(purchase_action["value"]) if purchase_action else 0
        purchase_value_action = next((a for a in (d.get("action_values") or []) if a["action_type"] == "purchase"), None)
        purchase_value = float(purchase_value_action["value"]) if purchase_value_action else 0.0
        spend = float(d.get("spend") or 0)
        roas = round(purchase_value / spend, 2) if spend > 0 else 0.0
        rows.append({
            "date":             d.get("date_start"),
            "campaign_id":      d.get("campaign_id", ""),
            "campaign_name":    d.get("campaign_name", ""),
            "adset_id":         d.get("adset_id", ""),
            "adset_name":       d.get("adset_name", ""),
            "ad_id":            d.get("ad_id", ""),
            "ad_name":          d.get("ad_name", ""),
            "spend":            spend,
            "impressions":      int(d.get("impressions") or 0),
            "clicks":           int(d.get("clicks") or 0),
            "reach":            int(d.get("reach") or 0),
            "purchases":        purchases,
            "purchase_value":   purchase_value,
            "purchase_roas":    roas,
            "account_currency": d.get("account_currency", "CAD"),
            "synced_at":        synced_at
        })
    return rows

# ── INSERT TO BIGQUERY ────────────────────────────────────────
def insert_to_bq(rows):
    if not rows:
        print("No rows to insert.")
        return
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["synced_at"] = pd.to_datetime(df["synced_at"])
    for col in ["campaign_id","campaign_name","adset_id","adset_name","ad_id","ad_name","account_currency"]:
        df[col] = df[col].fillna("").astype(str)
    df["spend"]          = pd.to_numeric(df["spend"], errors="coerce").fillna(0)
    df["impressions"]    = pd.to_numeric(df["impressions"], errors="coerce").fillna(0).astype(int)
    df["clicks"]         = pd.to_numeric(df["clicks"], errors="coerce").fillna(0).astype(int)
    df["reach"]          = pd.to_numeric(df["reach"], errors="coerce").fillna(0).astype(int)
    df["purchases"]      = pd.to_numeric(df["purchases"], errors="coerce").fillna(0).astype(int)
    df["purchase_value"] = pd.to_numeric(df["purchase_value"], errors="coerce").fillna(0)
    df["purchase_roas"]  = pd.to_numeric(df["purchase_roas"], errors="coerce").fillna(0)

    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND", schema=SCHEMA)
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"✅ {len(df)} rows inserted")

# ── RUN ───────────────────────────────────────────────────────
print("=" * 60)
print(f"Meta Ads Backfill: {START_DATE} → {END_DATE}")
print("=" * 60)

print("\nFetching Meta Ads data...")
data = fetch_meta_ads(START_DATE, END_DATE)
print(f"Total rows fetched: {len(data)}")

print("\nTransforming...")
rows = transform(data)

print("\nInserting to BigQuery...")
insert_to_bq(rows)

print("\n✅ Backfill complete!")
