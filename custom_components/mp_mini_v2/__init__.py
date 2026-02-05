# custom_components/mp_mini_v2/__init__.py
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.const import CONF_HOST
from .const import DOMAIN
from .coordinator import MPSelectMiniV2Coordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    
    # Create coordinator for this printer
    host = entry.data[CONF_HOST]
    coordinator = MPSelectMiniV2Coordinator(hass, host)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Forward the setup to the specified platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "number", "button"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "number", "button"]
    )
    
    # Shutdown coordinator
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    
    return unload_ok

async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: ConfigEntry, device_entry: DeviceEntry) -> bool:
    """Remove a config entry from a device."""
    return True