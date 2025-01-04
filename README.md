# homeassistant-whatspie-integration

Send Home Assistant notifications to WhatsApp using [WhatsPie](https://whatspie.com/).

## Features
- Send WhatsApp messages directly from Home Assistant.
- UI-based configuration for easy setup.
- Backward compatibility with YAML configuration.
- Supports sending messages to multiple recipients.
- Options flow to update configurations without reinstallation.
- Detailed error handling and logging for troubleshooting.

---

## Installation

### Manual Installation
1. Copy the `custom_components/whatspie` directory into Home Assistant's `config/custom_components/`.
2. Restart Home Assistant.

### HACS Installation
1. Add this GitHub repository as a custom repository in HACS: [HACS Custom Repositories](https://hacs.xyz/docs/faq/custom_repositories).
2. Install the **WhatsPie** integration via HACS.
3. Restart Home Assistant.

---

## Configuration

### Configuration via UI (Recommended)
1. Go to **Settings** > **Devices & Services** in Home Assistant.
2. Click **Add Integration** and search for **WhatsPie**.
3. Enter the required details:
   - **API Token**: Your WhatsPie API token.
   - **From Number**: Your WhatsPie phone number (without 0 or country code).
   - **Country Code**: Your country code prefix (e.g., `+62` for Indonesia).
4. Click **Submit** to complete the setup.

To modify settings, go to the **WhatsPie Integration** in the UI.

---

### YAML Configuration (Legacy)
You can still use YAML for setup if preferred. Add the following to your `configuration.yaml`:

```yaml
notify:
  - name: send_wa
    platform: whatspie
    api_token: "<your whatspie api token>"
    from_number: "<your whatspie phone number with country code, e.g., 62111222333>"
    country_code: "<your country code, e.g., 62>"
```

Restart Home Assistant after updating `configuration.yaml`.

---

## Usage

### Example Automation Configuration

#### Using the Notify Service created using UI
```
alias: Send Test Notification
description: ""
trigger: []
condition: []
action:
  - action: notify.whatspie_621122334455
    data:
      message: Test Notification -- HomeAssistant
      target:
        - "+621122335555"
mode: single
```

##### In target, change the number with the recepient number

#### Using the Notify Service configured using YAML
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

#### With Media Attachments (YAML only and if supported by WhatsPie API)
```yaml
alias: Send Media Notification
description: ""
trigger: []
condition: []
action:
  - service: notify.send_wa
    data:
      message: "Test Notification with media"
      target:
        - "+621122334455"
      data:
        media_url: "https://example.com/path/to/image.jpg"
mode: single
```

---

## Advanced Features

### Updating Configuration created in UI via Options Flow
- Navigate to **Settings** > **Devices & Services** > **WhatsPie Integration** > **Configure**.
- Update your API token, phone number, or country code directly from the UI.

### Logging
- Check Home Assistant logs for detailed debug information in case of issues:
  - API responses and errors.
  - Connection issues with WhatsPie API.

---

## Troubleshooting
- **Invalid API Token**: Ensure the API token is correctly copied from your WhatsPie account.
- **Connection Issues**: Verify network connectivity and that the WhatsPie API is accessible.
- **Message Not Delivered**: Check the phone number format, including country code.

---

## Contributions
Contributions, issues, and feature requests are welcome! Please check the [issue tracker](https://github.com/arifwn/homeassistant-whatspie-integration/issues) for existing issues or create a new one.

---
