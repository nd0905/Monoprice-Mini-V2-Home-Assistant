# custom_components/mp_mini_v2/number.py
import requests
from homeassistant.components.number import NumberEntity
from homeassistant.const import CONF_HOST, UnitOfTemperature
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    async_add_entities([
        MPSelectMiniV2Number(entry.entry_id, host, "Target Extruder Temperature", 0, 280, 0),
        MPSelectMiniV2Number(entry.entry_id, host, "Target Bed Temperature", 0, 80, 0),
    ])

class MPSelectMiniV2Number(NumberEntity):
    """Number entity for setting printer temperatures."""
    
    def __init__(self, entry_id, host, name, native_min_value, native_max_value, initial_value):
        self._entry_id = entry_id
        self._host = host
        self._attr_name = name
        self._attr_native_min_value = native_min_value
        self._attr_native_max_value = native_max_value
        self._attr_native_value = initial_value
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_icon = "mdi:thermometer"
        self._attr_mode = "box"
        self._attr_native_step = 1

    @property
    def unique_id(self):
        return f"{self._entry_id}_{self._attr_name}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Monoprice Select Mini V2",
            "manufacturer": "Monoprice",
            "model": "Select Mini V2",
        }

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = int(value)
        self.async_write_ha_state()
        
        # TODO: Send the value to the printer via API
        # Example: await self._send_to_printer(value)
