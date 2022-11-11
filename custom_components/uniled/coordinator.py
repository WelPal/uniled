"""UniLED Update Coordinator."""
from __future__ import annotations

from datetime import timedelta
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import UPDATE_SECONDS
from .lib.classes import UNILEDDevice
from .lib.ble_device import BLEAK_EXCEPTIONS

import logging

_LOGGER = logging.getLogger(__name__)

REQUEST_REFRESH_DELAY: Final = 2.0


class UNILEDUpdateCoordinator(DataUpdateCoordinator):
    """DataUpdateCoordinator to gather data for a specific UniLED device."""

    def __init__(self, hass: HomeAssistant, device: UNILEDDevice, entry: ConfigEntry) -> None:
        """Initialize DataUpdateCoordinator to gather data for specific device."""
        self.device = device
        self.title = entry.title
        self.entry = entry
        self.force_next_update = False
        super().__init__(
            hass,
            _LOGGER,
            name=f"{self.device.name}",
            update_interval=timedelta(seconds=UPDATE_SECONDS),
            # We don't want an immediate refresh since the device
            # takes a moment to reflect the state change
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=REQUEST_REFRESH_DELAY, immediate=False
            ),
        )

    async def _async_update_data(self) -> None:
        """Fetch all device and sensor data from api."""
        try:
            await self.device.update(force=self.force_next_update)
        except BLEAK_EXCEPTIONS as ex:
            raise UpdateFailed(str(ex)) from ex
        finally:
            self.force_next_update = False
