import logging
from datetime import timedelta

import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

DOMAIN = "pilot_live"
API_URL = "https://app.pilotlive.co.za/api/Mobile/Sitelist"
SCAN_INTERVAL = timedelta(seconds=300)


async def async_setup_entry(hass, entry, async_add_entities):
    session_id = entry.data["session_id"]

    coordinator = PilotLiveCoordinator(hass, session_id)
    await coordinator.async_config_entry_first_refresh()

    entities = [
        PilotLiveSensor(coordinator, site)
        for site in coordinator.data.get("SITE", [])
    ]

    async_add_entities(entities)

class PilotLiveCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session_id):
        self.session_id = session_id

        super().__init__(
            hass,
            _LOGGER,
            name="PilotLive",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        url = f"{API_URL}?sessionid={self.session_id}"
        session = async_get_clientsession(self.hass)

        try:
            async with async_timeout.timeout(10):
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return data

        except Exception as err:
            _LOGGER.error("Error fetching PilotLive data: %s", err)
            return {}


class PilotLiveSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, site_id, site_name):
        super().__init__(coordinator)
        self.site_id = site_id
        self._attr_name = f"PilotLive {site_name}"
        self._attr_unique_id = f"pilotlive_{site_id}"

    def _get_site(self):
        """Get latest site data from coordinator"""
        if not self.coordinator.data:
            return None

        for site in self.coordinator.data.get("SITE", []):
            if site["ID"] == self.site_id:
                return site

        return None

    @property
    def state(self):
        site = self._get_site()
        if site:
            return site.get("NAME")
        return None

    @property
    def extra_state_attributes(self):
        site = self._get_site()
        if not site:
            return {}

        return {
            row.get("DESC"): row.get("VALUE")
            for row in site.get("ROW", [])
        }
