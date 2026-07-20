import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .api import async_fetch_report, async_fetch_report_list, parse_report_rows
from .const import (
    ATTR_FROM_DATE,
    ATTR_REPORT_ID,
    ATTR_TO_DATE,
    DOMAIN,
    LAST_TRANSACTIONS_REPORT_ID,
    SERVICE_LAST_TRANSACTIONS_REPORT,
    SERVICE_REPORT,
    SERVICE_REPORT_LIST,
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

REPORT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_REPORT_ID): vol.Coerce(int),
        vol.Required(ATTR_FROM_DATE): cv.date,
        vol.Required(ATTR_TO_DATE): cv.date,
    }
)

REPORT_LIST_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
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


def _resolve_site(hass: HomeAssistant, entity_id: str):
    """Resolve an entity_id to its (session_id, site_id), or None if invalid."""
    entity_registry = er.async_get(hass)
    entity_entry = entity_registry.async_get(entity_id)
    if entity_entry is None or entity_entry.config_entry_id is None:
        _LOGGER.warning("%s is not a PilotLive entity", entity_id)
        return None

    entry_data = hass.data.get(DOMAIN, {}).get(entity_entry.config_entry_id)
    if not entry_data or "session_id" not in entry_data:
        _LOGGER.warning("No PilotLive session found for %s", entity_id)
        return None

    site_id = entity_entry.unique_id.removeprefix("pilotlive_")
    return entry_data["session_id"], site_id


def _make_report_handler(hass: HomeAssistant, get_report_id):
    """Build a service handler that fetches a report for each target entity.

    get_report_id(call) resolves the reportid to fetch, so this same handler
    backs both the fixed-report convenience services and the generic
    "report" service where the caller supplies report_id.
    """

    async def async_handle_report(call: ServiceCall) -> dict:
        results = {}

        for entity_id in call.data[ATTR_ENTITY_ID]:
            site = _resolve_site(hass, entity_id)
            if site is None:
                continue
            session_id, site_id = site
            report_id = get_report_id(call)

            try:
                raw_report = await async_fetch_report(
                    hass,
                    session_id,
                    site_id,
                    report_id,
                    call.data[ATTR_FROM_DATE].isoformat(),
                    call.data[ATTR_TO_DATE].isoformat(),
                )
            except Exception as err:  # noqa: BLE001
                _LOGGER.error(
                    "Error fetching report %s for %s: %s",
                    report_id,
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


def _make_report_list_handler(hass: HomeAssistant):
    async def async_handle_report_list(call: ServiceCall) -> dict:
        results = {}

        for entity_id in call.data[ATTR_ENTITY_ID]:
            site = _resolve_site(hass, entity_id)
            if site is None:
                continue
            session_id, site_id = site

            try:
                raw = await async_fetch_report_list(hass, session_id, site_id)
            except Exception as err:  # noqa: BLE001
                _LOGGER.error("Error fetching report list for %s: %s", entity_id, err)
                continue

            results[entity_id] = {"reports": raw.get("REPORT", [])}

        return results

    return async_handle_report_list


def _async_register_services(hass: HomeAssistant) -> None:
    if not hass.services.has_service(DOMAIN, SERVICE_TURNOVER_BY_DAY_REPORT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_TURNOVER_BY_DAY_REPORT,
            _make_report_handler(hass, lambda call: TURNOVER_BY_DAY_REPORT_ID),
            schema=TURNOVER_BY_DAY_REPORT_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_LAST_TRANSACTIONS_REPORT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_LAST_TRANSACTIONS_REPORT,
            _make_report_handler(hass, lambda call: LAST_TRANSACTIONS_REPORT_ID),
            schema=LAST_TRANSACTIONS_REPORT_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_REPORT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REPORT,
            _make_report_handler(hass, lambda call: call.data[ATTR_REPORT_ID]),
            schema=REPORT_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_REPORT_LIST):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REPORT_LIST,
            _make_report_list_handler(hass),
            schema=REPORT_LIST_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )
