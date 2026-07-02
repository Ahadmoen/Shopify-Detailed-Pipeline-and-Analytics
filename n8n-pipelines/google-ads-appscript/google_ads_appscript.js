var SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1DYBOsvuGO3zXDm3Y_lN2680EkzERxM7rLsw_xC9EVIk/edit?gid=0#gid=0';

function main() {
  var ss       = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
  var account  = AdsApp.currentAccount();
  var currency = account.getCurrencyCode();
  var syncedAt = new Date().toISOString();

  // ── Yesterday only ─────────────────────────────────────
  var yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  var dateStr = Utilities.formatDate(yesterday, account.getTimeZone(), 'yyyy-MM-dd');

  // ── Query: All campaigns (covers ALL types incl. PMAX) ─
  var campaignReport = AdsApp.report(
    'SELECT ' +
      'campaign.id, ' +
      'campaign.name, ' +
      'metrics.clicks, ' +
      'metrics.cost_micros, ' +
      'metrics.impressions, ' +
      'metrics.conversions, ' +
      'metrics.conversions_value, ' +
      'segments.date ' +
    'FROM campaign ' +
    'WHERE segments.date = \'' + dateStr + '\' ' +
    'AND campaign.status != REMOVED ' +
    'AND metrics.impressions > 0'
  );

  // ── Build campaign map ─────────────────────────────────
  var campaignMap = {};
  var rows = campaignReport.rows();

  while (rows.hasNext()) {
    var r  = rows.next();
    var id = r['campaign.id'];

    campaignMap[id] = {
      date:             r['segments.date'],
      campaign_id:      r['campaign.id'],
      campaign_name:    r['campaign.name'],
      ad_group_id:      '',
      ad_group_name:    '',
      ad_id:            '',
      ad_name:          '',
      spend:            parseFloat(r['metrics.cost_micros']) / 1000000 || 0,
      impressions:      parseInt(r['metrics.impressions']) || 0,
      clicks:           parseInt(r['metrics.clicks']) || 0,
      conversions:      Math.round((parseFloat(r['metrics.conversions']) || 0) * 100) / 100,
      conversion_value: Math.round((parseFloat(r['metrics.conversions_value']) || 0) * 100) / 100
    };
  }

  // ── Build output rows ──────────────────────────────────
  var headers = [
    'date', 'campaign_id', 'campaign_name',
    'ad_group_id', 'ad_group_name',
    'ad_id', 'ad_name',
    'spend', 'impressions', 'clicks',
    'conversions', 'conversion_value', 'roas',
    'account_currency', 'synced_at'
  ];

  var output = [];

  for (var id in campaignMap) {
    var c    = campaignMap[id];
    var roas = c.spend > 0 ? Math.round((c.conversion_value / c.spend) * 100) / 100 : 0;

    output.push([
      c.date,
      c.campaign_id,
      c.campaign_name,
      c.ad_group_id,
      c.ad_group_name,
      c.ad_id,
      c.ad_name,
      parseFloat(c.spend.toFixed(2)),
      c.impressions,
      c.clicks,
      c.conversions,
      c.conversion_value,
      roas,
      currency,
      syncedAt
    ]);
  }

  // ── Append to sheet ────────────────────────────────────
  var sheet = ss.getSheetByName('Google Ads Raw') || ss.insertSheet('Google Ads Raw');

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
  }

  if (output.length > 0) {
    sheet.getRange(sheet.getLastRow() + 1, 1, output.length, headers.length)
         .setValues(output);
  }

  Logger.log('Done — ' + output.length + ' campaigns written for ' + dateStr);
}
