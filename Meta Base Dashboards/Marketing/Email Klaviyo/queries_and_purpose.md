# Marketing — Email (Klaviyo) Tab

**Purpose:** Email campaign engagement. Filter: Date Range (send_time).
Note: Revenue shows $0 — Klaviyo conversion metric pending client configuration.

**Source view:** `final_reporting.fact_klaviyo_campaigns_v2`

---

## Total Email Sends
```sql
SELECT SUM(recipients) AS total_sends
FROM final_reporting.fact_klaviyo_campaigns_v2
WHERE {{send_time}}
```

## Avg Open Rate
```sql
SELECT ROUND(AVG(open_rate) * 100, 1) AS avg_open_rate
FROM final_reporting.fact_klaviyo_campaigns_v2
WHERE {{send_time}}
```

## Avg Click Rate
```sql
SELECT ROUND(AVG(click_rate) * 100, 1) AS avg_click_rate
FROM final_reporting.fact_klaviyo_campaigns_v2
WHERE {{send_time}}
```

## Campaign Performance Table
```sql
SELECT
  campaign_name, DATE(send_time) AS send_date,
  recipients, unique_opens, unique_clicks,
  ROUND(open_rate * 100, 1) AS open_rate_pct,
  ROUND(click_rate * 100, 1) AS click_rate_pct,
  unsubscribes, revenue
FROM final_reporting.fact_klaviyo_campaigns_v2
WHERE {{send_time}}
ORDER BY send_time DESC
```
