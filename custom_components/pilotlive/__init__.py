from homeassistant.core import HomeAssistant

DOMAIN = "pilotlive"

async def async_setup_entry(hass: HomeAssistant, entry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass, entry):
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return True
