# custom_components/mp_mini_v2/button.py
import logging
import requests
from homeassistant.components.button import ButtonEntity
from homeassistant.const import CONF_HOST
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    async_add_entities([
        MPSelectMiniV2Button(entry.entry_id, host, "Start Print"),
        MPSelectMiniV2Button(entry.entry_id, host, "Cancel Print"),
        MPSelectMiniV2Button(entry.entry_id, host, "Clear Extruder Target"),
        MPSelectMiniV2Button(entry.entry_id, host, "Clear Bed Target"),
        MPSelectMiniV2Button(entry.entry_id, host, "Set Extruder Target"),
        MPSelectMiniV2Button(entry.entry_id, host, "Set Bed Target"),
    ])

class MPSelectMiniV2Button(ButtonEntity):
    def __init__(self, entry_id, host, name):
        self._entry_id = entry_id
        self._host = host
        self._name = name

    @property
    def unique_id(self):
        return f"{self._entry_id}_{self._name.lower().replace(' ', '_')}"

    @property
    def name(self):
        return self._name

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Monoprice Select Mini V2",
            "manufacturer": "Monoprice",
            "model": "Select Mini V2",
        }

    async def async_press(self):
        if self._name == "Start Print":
            await self.start_print()
        elif self._name == "Cancel Print":
            await self.cancel_print()
        elif self._name == "Clear Extruder Target":
            await self.clear_extruder_temperature()
        elif self._name == "Clear Bed Target":
            await self.clear_bed_temperature()
        elif self._name == "Set Extruder Target":
            await self.set_extruder_temperature()
        elif self._name == "Set Bed Target":
            await self.set_bed_temperature()

    async def start_print(self):
        url = f"http://{self._host}/set?code=M565"
        _LOGGER.debug("Sending start print command: %s", url)
        await self.send_request(url)

    async def cancel_print(self):
        url = f"http://{self._host}/set?cmd={{P:X}}"
        _LOGGER.debug("Sending cancel print command: %s", url)
        await self.send_request(url)

    async def clear_extruder_temperature(self):
        url = f"http://{self._host}/set?cmd={{C:T0000}}"
        _LOGGER.debug("Sending clear extruder temperature command: %s", url)
        await self.send_request(url)

    async def clear_bed_temperature(self):
        url = f"http://{self._host}/set?cmd={{C:P000}}"
        _LOGGER.debug("Sending clear bed temperature command: %s", url)
        await self.send_request(url)

    async def set_extruder_temperature(self):
        value = self.hass.states.get("number.target_extruder_temperature").state
        url = f"http://{self._host}/set?cmd={{C:T0{int(float(value))}}}"
        _LOGGER.debug("Sending set extruder temperature command: %s", url)
        await self.send_request(url)
        await self.trigger_sensor_update("Target Extruder Temperature")

    async def set_bed_temperature(self):
        value = self.hass.states.get("number.target_bed_temperature").state
        url = f"http://{self._host}/set?cmd={{C:P0{int(float(value))}}}"
        _LOGGER.debug("Sending set bed temperature command: %s", url)
        await self.send_request(url)
        await self.trigger_sensor_update("Target Bed Temperature")

    async def send_request(self, url):
        try:
            await self.hass.async_add_executor_job(requests.get, url)
        except requests.RequestException as e:
            _LOGGER.error("Error sending request to %s: %s", url, e)

    async def trigger_sensor_update(self, sensor_name):
        """Trigger an update for the specified sensor."""
        sensor_entity_id = f"sensor.{self._entry_id}_{sensor_name.lower().replace(' ', '_')}"
        _LOGGER.debug("Triggering update for sensor: %s", sensor_entity_id)
        await self.hass.services.async_call(
            "homeassistant",
            "update_entity",
            {"entity_id": sensor_entity_id},
        )