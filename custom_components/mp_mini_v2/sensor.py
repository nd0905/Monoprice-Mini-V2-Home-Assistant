# custom_components/mp_mini_v2/sensor.py
import aiohttp
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_HOST, UnitOfTemperature
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    sensors = [
        MPSelectMiniV2Sensor(entry.entry_id, host, "Extruder Temperature", "temperature"),
        MPSelectMiniV2Sensor(entry.entry_id, host, "Extruder Target", "temperature"),
        MPSelectMiniV2Sensor(entry.entry_id, host, "Bed Temperature", "temperature"),
        MPSelectMiniV2Sensor(entry.entry_id, host, "Bed Target", "temperature"),
        MPSelectMiniV2Sensor(entry.entry_id, host, "Printer Status", "enum"),
        MPSelectMiniV2Sensor(entry.entry_id, host, "Printer Progress", None),
    ]
    async_add_entities(sensors)

class MPSelectMiniV2Sensor(SensorEntity):
    def __init__(self, entry_id, host, name, device_class):
        self._entry_id = entry_id
        self._host = host
        self._name = name
        self._device_class = device_class
        self._state = None
        self._async_unsub_update = None

    async def async_added_to_hass(self):
        self._async_unsub_update = async_track_time_interval(
            self.hass, self.async_update, SCAN_INTERVAL
        )
        await self.async_update()

    async def async_will_remove_from_hass(self) -> None:
        if self._async_unsub_update is not None:
            self._async_unsub_update()
            self._async_unsub_update = None

    @property
    def unique_id(self):
        return f"{self._entry_id}_{self._name}"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
    
    @property
    def device_class(self):
        return self._device_class
    
    @property
    def native_unit_of_measurement(self):
        if self._device_class == "temperature":
            return UnitOfTemperature.CELSIUS
    
    @property
    def options(self):
        """Return the list of available options for the Printer Status sensor."""
        if self._name == "Printer Status":
            return ["Idle", "Printing", "Unknown"]

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Monoprice Select Mini V2",
            "manufacturer": "Monoprice",
            "model": "Select Mini V2",
        }
    
    async def async_update(self, now=None) -> None:
        url = f"http://{self._host}/inquiry"

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(url) as response,
            ):
                response.raise_for_status()
                response_data = await response.text()
                if response_data:
                    self._state = self.parse_response(response_data)
                self.async_schedule_update_ha_state()

        except ConnectionError as e:
            _LOGGER.error("Error connecting to the 3D printer: %s", e)
        except aiohttp.ClientError as e:
            _LOGGER.error("HTTP error occurred: %s", e)
        except Exception as e:
            _LOGGER.exception("An error occurred: %s", e)
        return None

    def parse_response(self, data):
        import re
        if self._name == "Extruder Temperature":
            return re.findall(r'\d+', data)[0]
        if self._name == "Extruder Target":
            return re.findall(r'\d+', data)[1]
        elif self._name == "Bed Temperature":
            return re.findall(r'\d+', data)[2]
        elif self._name == "Bed Target":
            return re.findall(r'\d+', data)[3]
        elif self._name == "Printer Status":
            c = data[-1]
            return "Idle" if c == 'I' else "Printing" if c == 'P' else "Unknown"
        elif self._name == "Printer Progress":
            c = data[-1]
            return f"{re.findall(r'\d+', data)[4]}%" if c == 'P' else "Idle"
