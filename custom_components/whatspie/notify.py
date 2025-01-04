"""Send notifications as WhatsApp messages via WhatsPie"""

import httpx
import ssl
import certifi
import logging
import json
import requests

from homeassistant.const import CONF_API_TOKEN
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import async_get_current_platform
from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    BaseNotificationService,
    NotifyEntity,
)
from .const import CONF_API_TOKEN, CONF_FROM_NUMBER, CONF_COUNTRY_CODE

_LOGGER = logging.getLogger(__name__)

WHATSPIE_API_ENDPOINT = "https://api.whatspie.com"


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up WhatsPie notify platform from a config entry."""
    config_data = entry.data
    _LOGGER.debug("Config entry data received in notify platform: %s", config_data)

    if not all(
        k in config_data for k in [CONF_API_TOKEN, CONF_FROM_NUMBER, CONF_COUNTRY_CODE]
    ):
        _LOGGER.debug(
            "Missing required configuration data for WhatsPie notify platform."
        )
        return

    entity = WhatsPieNotificationService(
        hass=hass,
        api_token=config_data[CONF_API_TOKEN],
        from_number=config_data[CONF_FROM_NUMBER],
        country_code=config_data[CONF_COUNTRY_CODE],
    )

    await async_register_notify_service(hass, entity)
    async_add_entities([entity], update_before_add=False)


async def async_register_notify_service(hass: HomeAssistant, entity: NotifyEntity):
    """Register the WhatsPie notify entity with the notify service."""
    platform = async_get_current_platform()
    platform_name = platform.domain

    if platform_name != "notify":
        _LOGGER.error("Notify entity must be registered under the notify domain.")
        return

    notify_service_name = entity.name or "whatspie"
    hass.services.async_register(
        "notify",
        notify_service_name,
        entity.async_send_message,
    )

    _LOGGER.debug(
        "WhatsPie notify service '%s' registered successfully.", notify_service_name
    )


def sanitize_number(phone_number):
    """Sanitize a phone number and ensure proper formatting."""

    # Check if phone_number already includes the full country code
    if phone_number.startswith("+"):
        return phone_number.lstrip("+")

    # Remove leading '0' or '+' from the phone number
    if phone_number.startswith("0"):
        phone_number = phone_number[1:]
    elif phone_number.startswith("+"):
        phone_number = phone_number[1:]

    return phone_number


async def async_send_whatsapp_text_message(
    hass: HomeAssistant, to, message, api_token, from_number
) -> bool:
    """Send a WhatsApp message via WhatsPie API."""

    url = "https://api.whatspie.com/messages"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "receiver": sanitize_number(str(to)),
        "device": from_number,
        "message": message,
        "type": "chat",
        "simulate_typing": 1,
    }

    _LOGGER.debug("Sending WhatsPie message with payload: %s", payload)

    try:
        ssl_context = await hass.async_add_executor_job(
            lambda: ssl.create_default_context(cafile=certifi.where())
        )

        async with httpx.AsyncClient(verify=ssl_context) as client:
            response = await client.post(url, json=payload, headers=headers)

        if 200 <= response.status_code < 300:
            _LOGGER.debug("Message sent successfully to %s", to)
            return True

        _LOGGER.error(
            "WhatsPie API responded with error: %d - %s",
            response.status_code,
            response.text,
        )
        return False

    except httpx.RequestError as err:
        _LOGGER.error("Error connecting to WhatsPie API: %s", err)

    return False


class WhatsPieNotificationService(NotifyEntity):
    """Implement the notification service for WhatsPie."""

    def __init__(self, hass: HomeAssistant, api_token, from_number, country_code):
        """Initialize the service."""
        self.hass = hass
        self.api_token = api_token
        self.from_number = from_number
        self.country_code = country_code
        _LOGGER.debug("WhatsPieNotificationService initialized: %s", self.unique_id)

    @property
    def unique_id(self):
        """Return a unique identifier for this notification service."""
        return f"whatspie_{self.from_number}"

    @property
    def name(self):
        """Return the name of the notification service."""
        return f"whatspie_{self.from_number}"

    async def async_send_message(self, service_call: ServiceCall) -> None:
        """Send a WhatsApp message."""
        # Extract data from the service call
        message = service_call.data.get("message")
        target = service_call.data.get("target", [])

        _LOGGER.debug(
            "async_send_message called with message: %s, target: %s", message, target
        )

        # Validate that `message` and `target` are present
        if not message:
            _LOGGER.warning("No message specified for WhatsPie notification.")
            return

        if not target:
            _LOGGER.warning("No targets specified for WhatsPie notification.")
            return

        # Ensure target is always a list (even if a single string is provided)
        if isinstance(target, str):
            target = [target]

        # Iterate over each target and send the message
        for to in target:
            success = await async_send_whatsapp_text_message(
                self.hass, to, message, self.api_token, self.from_number
            )
            if not success:
                _LOGGER.error("Failed to send message to recipient: %s", to)


def sanitize_legacy(phone_number, country_code):
    if len(phone_number) == 0:
        return phone_number
    if phone_number[0] == "+":
        return phone_number[1:]
    if phone_number[0] == "0":
        return country_code + phone_number[1:]
    return phone_number


def send_whatsapp_legacy_message(rec, message, api_token, from_number, country_code):
    if not WHATSPIE_API_ENDPOINT:
        return False

    resp = requests.post(
        f"{WHATSPIE_API_ENDPOINT}/messages",
        data=json.dumps(
            {
                "receiver": sanitize_legacy(str(rec), country_code),
                "device": from_number,
                "message": message,
                "type": "chat",
                "simulate_typing": 1,
            }
        ),
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}",
        },
    )
    if resp.status_code == 200:
        return True

    _LOGGER.warning("WhatsPie HTTP API Response: %d - %s", resp.status_code, resp.text)

    return False


class WhatsPieLegacyNotificationService(BaseNotificationService):
    """Implement the notification service for the WhatsPie service."""

    def __init__(self, api_token, from_number, country_code):
        """Initialize the service."""
        self.api_token = api_token
        self.from_number = from_number
        self.country_code = country_code

    def send_message(self, message="", **kwargs):
        """Send message to specified target phone number."""
        targets = kwargs.get(ATTR_TARGET)
        data = kwargs.get(ATTR_DATA) or {}

        file_url = None
        if "media_url" in data:
            file_url = data["media_url"]

        if not targets:
            _LOGGER.info("At least 1 target is required")
            return

        for target in targets:
            send_whatsapp_legacy_message(
                target, message, self.api_token, self.from_number, self.country_code
            )


def get_service(hass, config, discovery_info=None):
    """Get the WhatsPie notification service."""
    return WhatsPieLegacyNotificationService(
        config["api_token"], config["from_number"], config["country_code"]
    )
