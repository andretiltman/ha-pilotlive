"""Helpers for calling the PilotLive Report API."""
import logging

import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import REPORT_URL

_LOGGER = logging.getLogger(__name__)


async def async_fetch_report(
    hass: HomeAssistant,
    session_id: str,
    site_id: str,
    report_id: int,
    from_date: str,
    to_date: str,
) -> dict:
    """Fetch a report from the PilotLive API and return the raw JSON payload."""
    params = {
        "reportid": report_id,
        "siteid": site_id,
        "fromdate": from_date,
        "todate": to_date,
        "sessionid": session_id,
    }

    session = async_get_clientsession(hass)

    async with async_timeout.timeout(30):
        async with session.get(REPORT_URL, params=params) as resp:
            resp.raise_for_status()
            # The API declares its content type as text/plain even though
            # the body is JSON, so content_type sniffing must be disabled.
            return await resp.json(content_type=None)


def parse_report_rows(data: dict) -> list[dict]:
    """Convert a report's HEADING/REPORTROW structure into a list of dicts.

    Column names are taken from HEADING so this works for any PilotLive
    report, not just Turnover by Day.
    """
    heading = {
        column["NAME"]: column["VALUE"]
        for column in data.get("HEADING", {}).get("COLUMNS", [])
    }

    rows = []
    for row in data.get("REPORTROW", []):
        parsed = {
            heading.get(column["NAME"], column["NAME"]): column["VALUE"]
            for column in row.get("COLUMNS", [])
        }
        parsed["highlight"] = row.get("HIGHLIGHT")
        parsed["seq"] = row.get("SEQ")
        rows.append(parsed)

    return rows
