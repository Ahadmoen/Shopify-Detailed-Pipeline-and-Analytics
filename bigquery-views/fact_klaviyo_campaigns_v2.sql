-- fact_klaviyo_campaigns_v2
-- Klaviyo email campaign performance with campaign name join.

CREATE OR REPLACE VIEW final_reporting.fact_klaviyo_campaigns_v2 AS
SELECT
  m.campaign_id,
  c.campaign_name,
  c.send_time,
  c.campaign_status,
  SAFE_CAST(m.recipients AS INT64)          AS recipients,
  SAFE_CAST(m.opens_unique AS INT64)        AS unique_opens,
  SAFE_CAST(m.clicks_unique AS INT64)       AS unique_clicks,
  SAFE_CAST(m.open_rate AS FLOAT64)         AS open_rate,
  SAFE_CAST(m.click_rate AS FLOAT64)        AS click_rate,
  SAFE_CAST(m.unsubscribes AS INT64)        AS unsubscribes,
  SAFE_CAST(m.revenue AS FLOAT64)           AS revenue,
  m.date                                     AS synced_date
FROM raw_marketing.klaviyo_campaign_metrics m
LEFT JOIN (
  SELECT *
  FROM raw_marketing.klaviyo_campaigns
  QUALIFY ROW_NUMBER() OVER (PARTITION BY campaign_id ORDER BY send_time DESC) = 1
) c ON m.campaign_id = c.campaign_id
QUALIFY ROW_NUMBER() OVER (PARTITION BY m.campaign_id ORDER BY m.date DESC) = 1;
