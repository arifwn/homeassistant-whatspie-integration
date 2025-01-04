import voluptuous as vol
import httpx
import logging
import ssl
import certifi

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.const import CONF_API_KEY
import homeassistant.helpers.config_validation as cv
from typing import Optional, Dict

from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_FROM_NUMBER,
    CONF_COUNTRY_CODE,
    CONF_ORIG_FROM_NUMBER,
    CONF_ORIG_COUNTRY_CODE,
)

_LOGGER = logging.getLogger(__name__)


class WhatsPieConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WhatsPie integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Sanitize country_code and from_number
                country_code = user_input[CONF_COUNTRY_CODE].lstrip("+")
                from_number = user_input[CONF_FROM_NUMBER].lstrip(
                    "0"
                )  # Remove leading "0" if present

                # Reassign sanitized values back to user_input
                user_input[CONF_COUNTRY_CODE] = country_code
                user_input[CONF_FROM_NUMBER] = from_number

                full_number = f"{country_code}{from_number}"

                await self._test_credentials(
                    user_input[CONF_API_TOKEN],
                    full_number,
                )

                user_input[CONF_ORIG_COUNTRY_CODE] = f"+{country_code}"
                user_input[CONF_ORIG_FROM_NUMBER] = user_input[CONF_FROM_NUMBER]
                user_input[CONF_COUNTRY_CODE] = f"{country_code}"
                user_input[CONF_FROM_NUMBER] = full_number

                _LOGGER.debug("Creating entry with sanitized values: %s", user_input)

                return self.async_create_entry(
                    title="WhatsPie Notification",
                    data=user_input,
                )
            except ValueError as err:
                if "Connection error" in str(err):
                    errors["base"] = "connection_error"
                elif "API validation error" in str(err):
                    errors["base"] = "auth_error"
                else:
                    errors["base"] = "unknown_error"
            except Exception:
                errors["base"] = "auth_error"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_TOKEN): cv.string,
                vol.Required(CONF_FROM_NUMBER): cv.string,
                vol.Required(CONF_COUNTRY_CODE): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _test_credentials(self, api_token, full_number):
        """Test the credentials by making an API call."""

        url = "https://api.whatspie.com/messages"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "receiver": full_number,  # Message self
            "device": full_number,
            "message": "Test message from Home Assistant - WhatsPie Integration",
            "type": "chat",
            "simulate_typing": 0,
        }

        _LOGGER.debug("Testing credentials with WhatsPie API at %s", url)

        def create_ssl_context():
            """Create SSL context (blocking)."""
            return ssl.create_default_context(cafile=certifi.where())

        ssl_context = await self.hass.async_add_executor_job(create_ssl_context)

        try:
            async with httpx.AsyncClient(verify=ssl_context) as client:
                response = await client.post(url, json=payload, headers=headers)

            if response.status_code != 200:
                _LOGGER.error(
                    "WhatsPie API validation failed: %s - %s",
                    response.status_code,
                    response.text,
                )
                raise ValueError(
                    f"API validation error: {response.status_code} - {response.text}"
                )

        except httpx.RequestError as err:
            _LOGGER.error("Connection error during WhatsPie validation: %s", err)
            raise ValueError(f"Connection error: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error during WhatsPie validation: %s", err)
            raise ValueError(f"Unexpected error: {err}") from err

        _LOGGER.debug("WhatsPie credentials validated successfully.")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Define the options flow."""
        return WhatsPieOptionsFlowHandler(config_entry)


class WhatsPieOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for WhatsPie."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Add validation here if necessary
            if not user_input[CONF_ORIG_FROM_NUMBER].isdigit():
                errors["base"] = "invalid_phone_number"
            elif not user_input[CONF_ORIG_COUNTRY_CODE]:
                errors["base"] = "invalid_country_code"
            elif not user_input[CONF_API_TOKEN]:
                errors["base"] = "invalid_api_token"
            else:
                # Compute the updated CONF_FROM_NUMBER
                full_number = f"{user_input[CONF_ORIG_COUNTRY_CODE].lstrip('+')}{user_input[CONF_ORIG_FROM_NUMBER]}"
                user_input[CONF_FROM_NUMBER] = full_number
                # Update entry with new options
                return self.async_create_entry(title="", data=user_input)

        # Fetch current values from options
        api_token = self.config_entry.options.get(
            CONF_API_TOKEN, self.config_entry.data.get(CONF_API_TOKEN)
        )
        from_number = self.config_entry.options.get(
            CONF_ORIG_FROM_NUMBER, self.config_entry.data.get(CONF_ORIG_FROM_NUMBER, "")
        )
        country_code = self.config_entry.options.get(
            CONF_ORIG_COUNTRY_CODE,
            self.config_entry.data.get(CONF_ORIG_COUNTRY_CODE, ""),
        )

        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_API_TOKEN,
                    default=self.config_entry.options.get(
                        CONF_API_TOKEN, self.config_entry.data.get(CONF_API_TOKEN)
                    ),
                ): cv.string,
                vol.Required(
                    CONF_ORIG_FROM_NUMBER,
                    default=self.config_entry.options.get(
                        CONF_ORIG_FROM_NUMBER,
                        self.config_entry.data.get(CONF_ORIG_FROM_NUMBER, ""),
                    ),
                ): cv.string,
                vol.Required(
                    CONF_ORIG_COUNTRY_CODE,
                    default=self.config_entry.options.get(
                        CONF_ORIG_COUNTRY_CODE,
                        self.config_entry.data.get(CONF_ORIG_COUNTRY_CODE, ""),
                    ),
                ): cv.string,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )