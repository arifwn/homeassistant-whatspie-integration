"""Send notifications as WhatsApp messages via WhatsPie"""

import logging
import json
import requests

_LOGGER = logging.getLogger(__name__)

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)

WHATSPIE_API_ENDPOINT = "https://api.whatspie.com"


def sanitize_number(phone_number, country_code):
    if len(phone_number) == 0:
        return phone_number
    if phone_number[0] == '+':
        return phone_number[1:]
    if phone_number[0] == '0':
        return country_code + phone_number[1:]
    return phone_number


def send_whatsapp_text_message(to, message, api_token, from_number, country_code):
    if not WHATSPIE_API_ENDPOINT:
        return False

    resp = requests.post(f'{WHATSPIE_API_ENDPOINT}/messages',
                     data=json.dumps({
                         'receiver': sanitize_number(str(to), country_code),
                         'device': from_number,
                         'message': message,
                         'type': 'chat',
                         'simulate_typing': 1
                     }),
                     headers={
                         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                         'Content-Type': 'application/json',
                         'Accept': 'application/json',
                         'Authorization': f'Bearer {api_token}'
                        }
                    )
    if resp.status_code == 200:
        return True
    
    _LOGGER.warning(
        "WhatsPie HTTP API Response: %d - %s", resp.status_code, resp.text
    )

    return False


class WhatsPieNotificationService(BaseNotificationService):
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
        if 'media_url' in data:
            file_url = data['media_url']

        if not targets:
            _LOGGER.info("At least 1 target is required")
            return

        for target in targets:
            send_whatsapp_text_message(target, message, self.api_token, self.from_number, self.country_code)


def get_service(hass, config, discovery_info=None):
    """Get the WhatsPie notification service."""
    return WhatsPieNotificationService(config['api_token'], config['from_number'], config['country_code'])

