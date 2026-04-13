import logging
import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME

DOMAIN = "pilot_live"
_LOGGER = logging.getLogger(__name__)

SEND_OTP_URL = "https://app.pilotlive.co.za/api/Mobile/SendOtp"
LOGON_URL = "https://app.pilotlive.co.za/api/Mobile/Logon"


class PilotLiveConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._data = {}

    # STEP 1: User enters details
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)

            await self._send_otp()

            return await self.async_step_pin()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("first_name"): str,
                vol.Required("last_name"): str,
                vol.Required("cellphone"): str,
            })
        )

    # STEP 2: Send OTP
    async def _send_otp(self):
        params = {
            "firstName": self._data["first_name"],
            "lastName": self._data["last_name"],
            "cellphone": self._data["cellphone"],
        }

        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(10):
                async with session.get(SEND_OTP_URL, params=params) as resp:
                    result = await resp.text()
                    _LOGGER.warning(f"SendOtp response: {result}")

    # STEP 3: Enter PIN
    async def async_step_pin(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)

            session_id = await self._login()

            if session_id:
                return self.async_create_entry(
                    title=f"PilotLive {self._data['cellphone']}",
                    data={
                        "session_id": session_id,
                        "cellphone": self._data["cellphone"],
                    }
                )

            return self.async_show_form(
                step_id="pin",
                data_schema=vol.Schema({
                    vol.Required("pin"): str,
                }),
                errors={"base": "invalid_pin"}
            )

        return self.async_show_form(
            step_id="pin",
            data_schema=vol.Schema({
                vol.Required("pin"): str,
            })
        )

    # STEP 4: Login and get SESSIONID
    async def _login(self):
        device_id = f"ha-{self._data['cellphone']}"

        params = {
            "cellphone": self._data["cellphone"],
            "pinno": self._data["pin"],
            "deviceid": device_id,
        }

        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(10):
                async with session.get(LOGON_URL, params=params) as resp:
                    data = await resp.json()
                    _LOGGER.warning(f"Logon response: {data}")

                    return data.get("SESSIONID")
