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
    def __init__(self, entry_id, host, name, native_min_value, native_max_value, initial_value):
        self._entry_id = entry_id
        self._host = host
        self._name = name
        self._attr_native_min_value = native_min_value
        self._attr_native_max_value = native_max_value
        self._value = initial_value
        self._native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._icon = "mdi:target"
        self._mode = "box"
        self._step = 1


    @property
    def unique_id(self):
        return f"{self._entry_id}_{self._name}"

    @property
    def name(self):
        return self._name

    @property
    def native_min_value(self):
        return self._attr_native_min_value

    @property
    def native_max_value(self):
        return self._attr_native_max_value

    @property
    def value(self):
        return int(self._value)

    @property
    def native_unit_of_measurement(self):
        return self._native_unit_of_measurement

    @property
    def icon(self):
        return self._icon
    
    @property
    def mode(self):
        return self._mode
    
    @property
    def step(self):
        return self._step

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Monoprice Select Mini V2",
            "manufacturer": "Monoprice",
            "model": "Select Mini V2",
        }

    async def async_set_value(self, value):
        self._value = int(value)
        self.async_write_ha_state()
