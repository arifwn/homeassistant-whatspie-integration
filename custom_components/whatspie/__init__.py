import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the integration using YAML (deprecated)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Whatspie integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the entry setup to the notify platform
    _LOGGER.debug("Forwarding setup to notify platform for WhatsPie integration.")
    await hass.config_entries.async_forward_entry_setups(entry, ["notify"])
    _LOGGER.debug("Setup forwarded to notify platform successfully.")

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "notify")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True