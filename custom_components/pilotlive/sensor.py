import logging
import re
from datetime import timedelta

import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

DOMAIN = "pilotlive"
API_URL = "https://app.pilotlive.co.za/api/Mobile/Sitelist"
SCAN_INTERVAL = timedelta(seconds=300)

METRIC_ICONS = {
    "Premium Version": "mdi:crown",
    "Total Monthly Sales": "mdi:cash-multiple",
    "Daily Sales": "mdi:cash",
    "Year on Year": "mdi:calendar-sync",
    "Projected Growth": "mdi:trending-up",
    "Open Tables": "mdi:table-furniture",
    "Discounts": "mdi:sale",
    "Ticket Claims": "mdi:receipt-text-check",
    "Voids": "mdi:cancel",
    "Payouts": "mdi:cash-refund",
    "Last Connection": "mdi:clock-outline",
}
DEFAULT_METRIC_ICON = "mdi:information-outline"


def _slugify(desc):
    return re.sub(r"[^a-z0-9]+", "_", desc.lower()).strip("_")


async def async_setup_entry(hass, entry, async_add_entities):
    session_id = entry.data["session_id"]

    coordinator = PilotLiveCoordinator(hass, session_id)
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for site in coordinator.data.get("SITE", []):
        entities.append(PilotLiveSensor(coordinator, site["ID"], site["NAME"]))
        for row in site.get("ROW", []):
            desc = row.get("DESC")
            if not desc:
                continue
            entities.append(
                PilotLiveMetricSensor(coordinator, site["ID"], site["NAME"], desc)
            )

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
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, site_id)},
            name=site_name,
            manufacturer="PilotLive",
        )

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
        if not site:
            return None
        
        for row in site.get("ROW", []):
            if row.get("DESC") == "Premium Version":
                return row.get("VALUE")

        return "Unknown"

    @property
    def extra_state_attributes(self):
        site = self._get_site()
        if not site:
            return {}

        return {
            row.get("DESC"): row.get("VALUE")
            for row in site.get("ROW", [])
        }

    @property
    def icon(self):
        site = self._get_site()
        if not site:
            return "mdi:store-off"

        for row in site.get("ROW", []):
            if row.get("DESC") == "Premium Version":
                if "OFFLINE" in row.get("VALUE", ""):
                    return "mdi:store-off"

        return "mdi:store"


class PilotLiveMetricSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, site_id, site_name, desc):
        super().__init__(coordinator)
        self.site_id = site_id
        self.desc = desc
        self._attr_name = f"PilotLive {site_name} {desc}"
        self._attr_unique_id = f"pilotlive_{site_id}_{_slugify(desc)}"
        self._attr_icon = METRIC_ICONS.get(desc, DEFAULT_METRIC_ICON)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, site_id)},
            name=site_name,
            manufacturer="PilotLive",
        )

    def _get_site(self):
        if not self.coordinator.data:
            return None

        for site in self.coordinator.data.get("SITE", []):
            if site["ID"] == self.site_id:
                return site

        return None

    @property
    def state(self):
        site = self._get_site()
        if not site:
            return None

        for row in site.get("ROW", []):
            if row.get("DESC") == self.desc:
                return row.get("VALUE")

        return None
