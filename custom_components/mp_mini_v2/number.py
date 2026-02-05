# custom_components/mp_mini_v2/coordinator.py
import logging
import asyncio
import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class MPSelectMiniV2Coordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from the printer once and share with all sensors."""

    def __init__(self, hass: HomeAssistant, host: str):
        """Initialize the coordinator."""
        self.host = host
        self._session = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from the printer."""
        url = f"http://{self.host}/inquiry"
        
        try:
            # Create session if it doesn't exist (reuse across updates)
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession()
            
            # Use async_timeout to prevent hanging
            async with async_timeout.timeout(5):  # 5 second timeout
                async with self._session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
                    
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout fetching data from printer at %s", self.host)
            raise UpdateFailed(f"Timeout connecting to printer")
        except aiohttp.ClientError as err:
            _LOGGER.warning("Error fetching data from printer: %s", err)
            raise UpdateFailed(f"Error communicating with printer: {err}")
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching printer data: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}")

    async def async_shutdown(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
