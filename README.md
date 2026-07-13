# HA Pilot Live [![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)

Pilot Live Sensor for Home Assistant

<img src="img/preview.png" width="auto" height="auto"/>

# Manual Install
<details>
<summary>Instructions</summary>

1. Download and unzip to your Home Assistant `config/custom_components` folder.
  <details>
  <summary>Screenshot</summary>
  
![image](https://user-images.githubusercontent.com/2578772/164681660-57d56fc4-4713-4be5-9ef1-bf2f7cf96b64.png)
  </details>
  
2. Restart Home Assistant.
</details>

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
