import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .api import async_fetch_report, parse_report_rows
from .const import (
    ATTR_FROM_DATE,
    ATTR_TO_DATE,
    DOMAIN,
    LAST_TRANSACTIONS_REPORT_ID,
    SERVICE_LAST_TRANSACTIONS_REPORT,
    SERVICE_TURNOVER_BY_DAY_REPORT,
    TURNOVER_BY_DAY_REPORT_ID,
)

_LOGGER = logging.getLogger(__name__)

TURNOVER_BY_DAY_REPORT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_FROM_DATE): cv.date,
        vol.Required(ATTR_TO_DATE): cv.date,
    }
)

LAST_TRANSACTIONS_REPORT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_FROM_DATE): cv.date,
        vol.Required(ATTR_TO_DATE): cv.date,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    _async_register_services(hass)

    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])


def _make_report_handler(hass: HomeAssistant, report_id: int, report_label: str):
    async def async_handle_report(call: ServiceCall) -> dict:
        entity_registry = er.async_get(hass)
        results = {}

        for entity_id in call.data[ATTR_ENTITY_ID]:
            entity_entry = entity_registry.async_get(entity_id)
            if entity_entry is None or entity_entry.config_entry_id is None:
                _LOGGER.warning("%s is not a PilotLive entity", entity_id)
                continue

            entry_data = hass.data.get(DOMAIN, {}).get(entity_entry.config_entry_id)
            if not entry_data or "session_id" not in entry_data:
                _LOGGER.warning("No PilotLive session found for %s", entity_id)
                continue

            site_id = entity_entry.unique_id.removeprefix("pilotlive_")

            try:
                raw_report = await async_fetch_report(
                    hass,
                    entry_data["session_id"],
                    site_id,
                    report_id,
                    call.data[ATTR_FROM_DATE].isoformat(),
                    call.data[ATTR_TO_DATE].isoformat(),
                )
            except Exception as err:  # noqa: BLE001
                _LOGGER.error(
                    "Error fetching %s report for %s: %s",
                    report_label,
                    entity_id,
                    err,
                )
                continue

            results[entity_id] = {
                "report_name": raw_report.get("REPORTNAME"),
                "from_date": raw_report.get("FROMDATE"),
                "to_date": raw_report.get("TODATE"),
                "rows": parse_report_rows(raw_report),
            }

        return results

    return async_handle_report


def _async_register_services(hass: HomeAssistant) -> None:
    if not hass.services.has_service(DOMAIN, SERVICE_TURNOVER_BY_DAY_REPORT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_TURNOVER_BY_DAY_REPORT,
            _make_report_handler(hass, TURNOVER_BY_DAY_REPORT_ID, "turnover by day"),
            schema=TURNOVER_BY_DAY_REPORT_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_LAST_TRANSACTIONS_REPORT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_LAST_TRANSACTIONS_REPORT,
            _make_report_handler(hass, LAST_TRANSACTIONS_REPORT_ID, "last transactions"),
            schema=LAST_TRANSACTIONS_REPORT_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )
