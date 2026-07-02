-- fact_marketing_v2
-- Meta Ads + Google Ads unioned into one marketing performance view.

CREATE OR REPLACE VIEW final_reporting.fact_marketing_v2 AS
SELECT
  'Meta'                                        AS source,
  date,
  campaign_id,
  campaign_name,
  adset_id                                      AS ad_group_id,
  adset_name                                    AS ad_group_name,
  ad_id,
  ad_name,
  CAST(spend AS FLOAT64)                        AS spend,
  CAST(impressions AS INT64)                    AS impressions,
  CAST(clicks AS INT64)                         AS clicks,
  reach,
  CAST(purchases AS INT64)                      AS conversions,
  CAST(purchase_value AS FLOAT64)               AS conversion_value,
  CAST(purchase_roas AS FLOAT64)                AS roas,
  account_currency
FROM raw_marketing.meta_ads

UNION ALL

SELECT
  'Google'                                      AS source,
  date,
  campaign_id,
  campaign_name,
  ad_group_ad                                   AS ad_group_id,
  ad_group_name,
  ad_id,
  ad_name,
  CAST(spend AS FLOAT64)                        AS spend,
  CAST(impressions AS INT64)                    AS impressions,
  CAST(clicks AS INT64)                         AS clicks,
  NULL                                          AS reach,
  CAST(conversions AS INT64)                    AS conversions,
  CAST(conversion_value AS FLOAT64)             AS conversion_value,
  SAFE_CAST(roas AS FLOAT64)                    AS roas,
  account_currency_code                         AS account_currency
FROM raw_marketing.google_ads;
