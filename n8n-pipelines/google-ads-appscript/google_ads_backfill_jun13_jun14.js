var SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1DYBOsvuGO3zXDm3Y_lN2680EkzERxM7rLsw_xC9EVIk/edit?gid=0#gid=0';

var BACKFILL_DATES = ['2026-06-13', '2026-06-14'];

function main() {
  var ss       = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
  var account  = AdsApp.currentAccount();
  var currency = account.getCurrencyCode();
  var syncedAt = new Date().toISOString();

  var headers = [
    'date', 'campaign_id', 'campaign_name',
    'ad_group_id', 'ad_group_name',
    'ad_id', 'ad_name',
    'spend', 'impressions', 'clicks',
    'conversions', 'conversion_value', 'roas',
    'account_currency', 'synced_at'
  ];

  var sheet = ss.getSheetByName('Google Ads Raw') || ss.insertSheet('Google Ads Raw');

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
  }

  // ── Loop through each backfill date ────────────────────
  for (var d = 0; d < BACKFILL_DATES.length; d++) {
    var dateStr = BACKFILL_DATES[d];
    var output  = [];

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

    var rows = campaignReport.rows();

    while (rows.hasNext()) {
      var r    = rows.next();
      var spend = parseFloat(r['metrics.cost_micros']) / 1000000 || 0;
      var convValue = Math.round((parseFloat(r['metrics.conversions_value']) || 0) * 100) / 100;
      var roas  = spend > 0 ? Math.round((convValue / spend) * 100) / 100 : 0;

      output.push([
        r['segments.date'],
        r['campaign.id'],
        r['campaign.name'],
        '', '', '', '',
        parseFloat(spend.toFixed(2)),
        parseInt(r['metrics.impressions']) || 0,
        parseInt(r['metrics.clicks']) || 0,
        Math.round((parseFloat(r['metrics.conversions']) || 0) * 100) / 100,
        convValue,
        roas,
        currency,
        syncedAt
      ]);
    }

    if (output.length > 0) {
      sheet.getRange(sheet.getLastRow() + 1, 1, output.length, headers.length)
           .setValues(output);
    }

    Logger.log(dateStr + ' — ' + output.length + ' campaigns written');
  }

  Logger.log('Backfill complete for: ' + BACKFILL_DATES.join(', '));
}
