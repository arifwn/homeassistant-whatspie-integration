import logging
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_API_TOKEN, CONF_FROM_NUMBER, CONF_COUNTRY_CODE

_LOGGER = logging.getLogger(__name__)


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_TOKEN): cv.string,
                vol.Required(CONF_FROM_NUMBER): cv.string,
                vol.Required(CONF_COUNTRY_CODE): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,  # Allow additional keys in YAML
)


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
