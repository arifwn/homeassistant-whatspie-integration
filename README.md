# homeassistant-whatspie-integration
Send Home Assistant notifications to WhatsApp using [WhatsPie](https://whatspie.com/)

## Installation
- Copy `custom_components/whatspie` directory into Home Assistant's `config/custom_components/`
- Create a new notification service in your `configuration.yaml` file:
```yaml
notify:
  - name: send_wa
    platform: whatspie
    api_token: "<your whatspie api token>"
    from_number: "<your whatspie phone number with country code prefix, e.g. 62111222333>"
    country_code: "<your country code prefix, e.g. 62>"
```
- restart Home Assistant: Go to "Developer Tools", then press "Check Configuration" followed by "Restart"

## Usage

Example automation configuration:
```yaml
alias: Send Test Notification
description: ""
trigger: []
condition: []
action:
  - service: notify.send_wa
    data:
      message: Test Notification -- HomeAssistant
      target:
        - "+621122334455"
mode: single
```
