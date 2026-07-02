# Marketing — Paid Media Tab

**Purpose:** Meta and Google Ads performance. Filter: Date Range.
Note: Meta Ads account (act_2626840940790152) currently returns no data — pending correct client credentials.

**Source view:** `final_reporting.fact_marketing_v2`

---

## Total Marketing Spend
```sql
SELECT ROUND(SUM(spend), 2) AS total_spend
FROM final_reporting.fact_marketing_v2
WHERE {{date}}
```

## Spend by Channel
```sql
SELECT source, ROUND(SUM(spend), 2) AS spend
FROM final_reporting.fact_marketing_v2
WHERE {{date}}
GROUP BY source
```

## ROAS by Channel
```sql
SELECT source, ROUND(SUM(conversion_value) / NULLIF(SUM(spend), 0), 2) AS roas
FROM final_reporting.fact_marketing_v2
WHERE {{date}}
GROUP BY source
```

## Daily Spend by Channel
```sql
SELECT date, source, ROUND(SUM(spend), 2) AS spend
FROM final_reporting.fact_marketing_v2
WHERE {{date}}
GROUP BY date, source ORDER BY date
```

## Conversions by Channel
```sql
SELECT source, SUM(conversions) AS conversions
FROM final_reporting.fact_marketing_v2
WHERE {{date}}
GROUP BY source
```
