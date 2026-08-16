# HA Pilot Live [![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)

Pilot Live Sensor for Home Assistant

<img src="img/preview.png" width="auto" height="auto"/>

# Installation

## HACS (recommended)

This integration isn't in the default HACS store yet, so it needs to be added as a custom repository first.

1. Make sure [HACS](https://hacs.xyz/docs/use/) is installed in your Home Assistant instance.
2. In Home Assistant, go to **HACS**.
3. Click the three-dot menu (⋮) in the top right corner and select **Custom repositories**.
4. In the dialog, add:
   - **Repository:** `https://github.com/andretiltman/ha-pilotlive`
   - **Type:** `Integration`
5. Click **Add**.
6. Search HACS for **PilotLive**, open it, and click **Download**.
7. Restart Home Assistant.
8. Go to **Settings → Devices & Services → Add Integration**, search for **PilotLive**, and follow the prompts to set it up.

## Manual Install

1. Download and unzip to your Home Assistant `config/custom_components` folder.
  <details>
  <summary>Screenshot</summary>
  
![image](https://user-images.githubusercontent.com/2578772/164681660-57d56fc4-4713-4be5-9ef1-bf2f7cf96b64.png)
  </details>
  
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration**, search for **PilotLive**, and follow the prompts to set it up.


# Using with Claude terminal (heytcass/home-assistant-addons)

If you're running Claude in a terminal against your Home Assistant instance
via the [heytcass/home-assistant-addons](https://github.com/heytcass/home-assistant-addons)
`ha_call_service` tool, add the following to your `CLAUDE.md` so Claude knows
how to pull PilotLive reports for stores you own or manage:

```markdown
## PilotLive reports

Pulls reporting information for Stores that I Own or Manage

Target entity: `sensor.pilotlive_{store_name}`. The `pilotlive` domain exposes 4 services via `ha_call_service` (pass `return_response: true` to get the data back):

- `pilotlive.report_list` — no params. Lists every available report as `{NAME, ID, AccessRoles, SortOrder}`. Run this first if unsure of a report's ID.
- `pilotlive.report` — `report_id` (number), `from_date`, `to_date` (YYYY-MM-DD). Fetches any report by ID.
- `pilotlive.turnover_by_day_report` — `from_date`, `to_date`. Shortcut for report ID 1 (also what the Work dashboard's "Turnover by Day" markdown card reads from `sensor.pilotlive_{store_name}_turnover_by_day`).
- `pilotlive.last_transactions_report` — `from_date`, `to_date`. Shortcut for report ID 48.

Common report IDs (from `report_list`, subject to change — re-run it if one seems missing): Last Transactions=48, Turnover by Day=1, Turnover Comparison=33, Turnover by Month=2, Trading Patterns=13, Bill Average=16, PLU Sales=17, Department Sales=22, Waiter Sales=8, Waiter Tips=46, Staff Working=11, Main Meal Statistics=15, Open Table Duration=37, Open Tables (2hrs+)=38, Order Messages=21, Cashup Variances=6, Prep Variances=7, Discounts and Voids=9, Sales Returns=18, Cash Payout Audit=29, Cash Payout Listing=28, Purchases by Day=3, Purchases Detail by Day=12, Supplier Payments=4, Purchases by Supplier=5, Last Purchase Price=74, Supplier Phonebook=10, Bulk Portion Details=31, Bulk Yields=30, Bulksheet Variances=32, Stock Valuation=23, Income Statement=14, Theoretical Income Statement=24, Banking=26, Tender Type=40, Loyalty Sales=19, Loyalty Swipe Rate=20, Backup Status=25.

Example: `ha_call_service(domain="pilotlive", service="report", entity_id="sensor.pilotlive_{store_name}", data={"report_id": 3, "from_date": "2026-07-28", "to_date": "2026-08-11"}, return_response=True)` → rows come back under `service_response.<entity_id>.rows`, usually with `Sub Total`/`Grand Total` marker rows (`highlight` field flags them).
```

Replace `{store_name}` with your own entity's store name slug (see [Discovering available reports](#discovering-available-reports) above for how to find your entity_id).


# Lovelace Card Example

Each store is exposed as a sensor whose state is the store's Premium Version status, with the rest of the store's data (Online, Total Monthly Sales, Daily Sales, Year on Year, Projected Growth, Open Tables, Discounts, Ticket Claims, Voids, Payouts, Last Connection) available as attributes.

A ready-to-use [entities card](https://www.home-assistant.io/dashboards/entities/) example is provided in [`lovelace-examples/store-card.yaml`](lovelace-examples/store-card.yaml) — built entirely with built-in Home Assistant Lovelace features, no extra HACS frontend cards required.

```yaml
type: entities
title: PilotLive Valley Brewery
state_color: true
entities:
  - entity: sensor.pilotlive_valley_brewery
    name: Premium Version
    icon: mdi:store
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Online"
    name: Online
    icon: mdi:wifi
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Total Monthly Sales"
    name: Total Monthly Sales
    prefix: "R "
    icon: mdi:cash-multiple
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Daily Sales"
    name: Daily Sales
    prefix: "R "
    icon: mdi:cash
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Year on Year"
    name: Year on Year
    suffix: "%"
    icon: mdi:chart-line
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Projected Growth"
    name: Projected Growth
    suffix: "%"
    icon: mdi:trending-up
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Open Tables"
    name: Open Tables
    icon: mdi:table-furniture
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Discounts"
    name: Discounts
    prefix: "R "
    icon: mdi:sale
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Ticket Claims"
    name: Ticket Claims
    prefix: "R "
    icon: mdi:receipt
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Voids"
    name: Voids
    prefix: "R "
    icon: mdi:cancel
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Payouts"
    name: Payouts
    prefix: "R "
    icon: mdi:cash-refund
  - type: attribute
    entity: sensor.pilotlive_valley_brewery
    attribute: "Last Connection"
    name: Last Connection
    icon: mdi:clock-outline
```

Replace `sensor.pilotlive_valley_brewery` with the entity_id of your own store sensor, then add the card via **Edit Dashboard → Add Card → Manual** in Lovelace.

# Reports

Reports are exposed as Home Assistant services that you call against a store's
sensor entity, returning the report data as [service response data](https://www.home-assistant.io/docs/scripts/perform-actions/#use-templates-to-determine-data-in-a-service-call).

`pilotlive.turnover_by_day_report` and `pilotlive.last_transactions_report`
below are convenience services for two commonly used reports. For any other
report, use the generic `pilotlive.report` service together with
`pilotlive.report_list` to look up its `report_id`.

## Discovering available reports

Call `pilotlive.report_list` targeting one or more PilotLive sensor entities
to get the reports available for that site, as returned by PilotLive's
`ReportList` API:

```yaml
action: pilotlive.report_list
target:
  entity_id: sensor.pilotlive_valley_brewery
```

```yaml
sensor.pilotlive_valley_brewery:
  reports:
    - NAME: Last Transactions
      ID: "48"
      AccessRoles: "ADMIN,USER,BETA,MANAGER"
      SortOrder: -1
    - NAME: Turnover by Day
      ID: "1"
      AccessRoles: "ADMIN,USER,BETA,MANAGER"
      SortOrder: 1
    # ... one entry per report available to this site/session
```

The reports available depend on your site and user role. As a reference,
these are the reports one PilotLive account had access to at the time of
writing:

| Report ID | Name |
| ---: | --- |
| 48 | Last Transactions |
| 1 | Turnover by Day |
| 33 | Turnover Comparison |
| 2 | Turnover by Month |
| 13 | Trading Patterns |
| 16 | Bill Average |
| 17 | PLU Sales |
| 22 | Department Sales |
| 8 | Waiter Sales |
| 46 | Waiter Tips |
| 15 | Main Meal Statistics |
| 37 | Open Table Duration |
| 38 | Open Tables (2 hours+) |
| 11 | Staff Working |
| 6 | Cashup Variances |
| 7 | Prep Variances |
| 9 | Discounts and Voids |
| 18 | Sales Returns |
| 3 | Purchases by Day |
| 4 | Supplier Payments |
| 5 | Purchases by Supplier |
| 12 | Purchases Detail by Day |
| 31 | Bulk Portion Details |
| 30 | Bulk Yields |
| 32 | Bulksheet Variances |
| 29 | Cash Payout Audit |
| 28 | Cash Payout Listing |
| 14 | Income Statement |
| 24 | Theoretical Income Statement |
| 21 | Order Messages |
| 74 | Last Purchase Price |
| 10 | Supplier Phonebook |
| 19 | Loyalty Sales |
| 20 | Loyalty Swipe Rate |
| 23 | Stock Valuation |
| 25 | Backup Status |
| 26 | Banking |
| 40 | Tender Type |

## Any report by ID

Call `pilotlive.report` targeting one or more PilotLive sensor entities with
a `report_id`, `from_date` and `to_date` to fetch any report from the table
above (or any other report_id your site has access to):

```yaml
action: pilotlive.report
target:
  entity_id: sensor.pilotlive_valley_brewery
data:
  report_id: 22
  from_date: "2024-09-01"
  to_date: "2024-09-30"
```

The response has the same shape as every other report service — keyed by
entity_id with the report name, the date range and a `rows` list, with column
names determined by whatever `report_id` you requested.

## Turnover by Day

Call `pilotlive.turnover_by_day_report` targeting one or more PilotLive sensor
entities with a `from_date` and `to_date` to get each day's sales:

```yaml
action: pilotlive.turnover_by_day_report
target:
  entity_id: sensor.pilotlive_valley_brewery
data:
  from_date: "2024-09-01"
  to_date: "2024-09-30"
```

The response is keyed by entity_id and includes the report name, the date
range and a `rows` list, e.g.:

```yaml
sensor.pilotlive_valley_brewery:
  report_name: Turnover by Day
  from_date: "2024-09-01"
  to_date: "2024-09-30"
  rows:
    - Date: "20/09/24"
      Day: Friday
      Sales Excl: "150.43"
      Sales Incl: "173.00"
      Discnt Incl: "0.00"
      highlight: "0"
      seq: "1"
    - Date: Total
      Day: ""
      Sales Excl: "21246.87"
      Sales Incl: "24433.90"
      Discnt Incl: "-7.00"
      highlight: "2"
      seq: "18"
```

### Dashboard example

Service calls with response data aren't available directly as Lovelace card
sources, so the response has to be cached on an entity first. The example in
[`lovelace-examples/turnover-by-day-sensor.yaml`](lovelace-examples/turnover-by-day-sensor.yaml)
is a trigger-based template sensor (add it under `configuration.yaml`) that
calls `pilotlive.turnover_by_day_report` for the trailing 30 days on startup
and every 6 hours, caching the rows as an attribute.

[`lovelace-examples/turnover-by-day-card.yaml`](lovelace-examples/turnover-by-day-card.yaml)
is a Markdown card — again, no extra HACS frontend cards required — that
renders those cached rows as a table, with the Total row shown in bold.

Replace `sensor.pilotlive_valley_brewery` and
`sensor.pilotlive_valley_brewery_turnover_by_day` in both files with your own
entity_ids, then add the card via **Edit Dashboard → Add Card → Manual** in
Lovelace.

### Charting it with the PilotLive Graph Card

[`lovelace/pilotlive-graph-card.js`](lovelace/pilotlive-graph-card.js) is a custom
Lovelace card — `custom:pilotlive-graph-card` — that renders a column or line
chart from any cached PilotLive report sensor's `rows` attribute. It doesn't
hardcode a date format, column name, or store, so the same card works for
Turnover by Day, Turnover by Month, Turnover Comparison, Bill Average, or any
other report you've cached with a trigger-based template sensor as described
above.

**Installing the card:**

1. Copy `lovelace/pilotlive-graph-card.js` from this repo into your Home
   Assistant `config/www/` folder (create it if it doesn't exist).
2. In Home Assistant, go to **Settings → Dashboards**, click the three-dot
   menu (⋮) in the top right, and select **Resources**.
3. Click **Add Resource**, set the URL to `/local/pilotlive-graph-card.js`,
   and set the resource type to **JavaScript Module**.
4. Refresh your browser (a hard refresh may be needed to clear the cache).
5. Add the card via **Edit Dashboard → Add Card → Manual** and use a config
   like [`lovelace-examples/turnover-by-day-graph-card.yaml`](lovelace-examples/turnover-by-day-graph-card.yaml):

```yaml
type: custom:pilotlive-graph-card
entity: sensor.pilotlive_valley_brewery_turnover_by_day
title: Turnover by Day — Valley Brewery
date_field: Date
value_field: Sales Incl
chart_type: column
color: "#2a78d6"
y_prefix: "R "
```

Replace `entity` with your own cached report sensor's entity_id. Available
options:

| Option | Default | Description |
| --- | --- | --- |
| `entity` | *(required)* | The sensor whose `rows` attribute holds the report data. |
| `title` | entity's `friendly_name` | Card title. |
| `date_field` | `Date` | Row key used for the x-axis label. |
| `value_field` | `Sales Incl` | Row key charted on the y-axis. |
| `chart_type` | `column` | `column` or `line`. |
| `color` | `#2a78d6` | Bar/line color. |
| `y_prefix` | `R ` | Prefix shown on y-axis labels and tooltips. |
| `exclude_highlight` | `["2"]` | Row `highlight` values to skip (PilotLive marks subtotal/grand-total rows with `"2"`). |
| `max_labels` | `10` | Thins x-axis labels on wide date ranges so they don't overlap. |

The x-axis value (`date_field`) is used as-is for each bar's label. If every
row's value parses as a recognised date shape (`dd/mm/yy(yy)`,
`yyyy-mm-dd`, or `Mon yyyy`), rows are sorted chronologically; otherwise
rows are left in report order (e.g. a report already ranked by period or
category name).

## Last Transactions

Call `pilotlive.last_transactions_report` targeting one or more PilotLive
sensor entities with a `from_date` and `to_date` to get the most recent
transactions for the period:

```yaml
action: pilotlive.last_transactions_report
target:
  entity_id: sensor.pilotlive_valley_brewery
data:
  from_date: "2024-09-01"
  to_date: "2024-09-30"
```

The response has the same shape as Turnover by Day — keyed by entity_id with
the report name, the date range and a `rows` list. The column names in each
row depend on how PilotLive lays out the Last Transactions report (report ID
`48`), but every row still carries `highlight` and `seq` alongside the report's
own columns, e.g.:

```yaml
sensor.pilotlive_valley_brewery:
  report_name: Last Transactions
  from_date: "2024-09-01"
  to_date: "2024-09-30"
  rows:
    - Date: "20/09/24"
      Time: "14:32"
      Amount: "24.50"
      highlight: "0"
      seq: "1"
```

### Dashboard example

[`lovelace-examples/last-transactions-sensor.yaml`](lovelace-examples/last-transactions-sensor.yaml)
is a trigger-based template sensor, same pattern as the Turnover by Day one,
that calls `pilotlive.last_transactions_report` for the trailing 30 days on
startup and every 6 hours, caching the rows as an attribute.

[`lovelace-examples/last-transactions-card.yaml`](lovelace-examples/last-transactions-card.yaml)
is a Markdown card that renders those cached rows as a table, building its
header from whatever columns the report returns rather than hardcoding
column names, since those depend on your PilotLive report layout.

Replace `sensor.pilotlive_valley_brewery` and
`sensor.pilotlive_valley_brewery_last_transactions` in both files with your
own entity_ids, then add the card via **Edit Dashboard → Add Card → Manual**
in Lovelace.

