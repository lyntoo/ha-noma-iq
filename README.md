# Noma iQ — Home Assistant Integration

Unofficial Home Assistant integration for the **Noma iQ** air conditioner (Canadian Tire), using the Ayla Networks cloud API.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=lyntoo&repository=ha-noma-iq&category=integration)

> **Tested on:** Noma iQ portable and window AC units (`port-ac`, `win-ac`)

## Features

- Full climate entity (on/off, cool / dry / fan-only modes)
- Fan speed: auto / low / medium / high
- Swing control
- Target temperature (16–32 °C)
- Ambient temperature sensor
- 30-second polling

## Prerequisites — Ayla App Credentials

This integration requires the **Ayla App ID and App Secret** registered by Canadian Tire for the Noma iQ app. These are embedded in the official Android APK and must be extracted by the user.

### How to extract them

1. Download the official **Noma iQ APK** (e.g. from APKPure or directly from your device)
2. Run:
   ```bash
   unzip -d noma_apk NOMA_iQ.apk
   strings noma_apk/classes.dex | grep -A2 -B2 "ctc-noma"
   ```
3. You will see two consecutive values — the App ID and the App Secret

Alternatively, use **jadx-gui** (graphical Java decompiler): open the APK, search for `app_id`, and read the adjacent values.

> ⚠️ These credentials belong to Canadian Tire and could be revoked at any time. If the integration stops authenticating, re-extract from a newer APK version.

## Installation

### HACS (recommended)

Click the badge below to add the repository directly to HACS:

[![Open your Home Assistant instance and add the Noma iQ custom repository.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/custom_repository/?repository=https%3A%2F%2Fgithub.com%2Flyntoo%2Fha-noma-iq&category=integration)

Or manually: in HACS, add this repository as a custom repository (Integration), install **Noma iQ**, then restart Home Assistant.

### Manual

Copy the `custom_components/noma_iq/` folder into your HA `config/custom_components/` directory, then restart.

## Configuration

1. Go to **Settings → Integrations → Add Integration**
2. Search for **Noma iQ**
3. Enter:
   - Your Canadian Tire / Noma iQ **email and password**
   - The **Ayla App ID** and **Ayla App Secret** extracted from the APK
4. Select your AC unit if you have more than one

## Supported models

| `oem_model` | Description |
|---|---|
| `win-ac` | Window AC |
| `port-ac` | Portable AC |
| `port8k-ac` | Portable AC 8000 BTU |
| `port10k-ac` | Portable AC 10000 BTU |

Other Noma iQ models using the Ayla platform may work — open an issue to add your `oem_model`.

## Disclaimer

This is an unofficial, community-developed integration. It is not affiliated with or endorsed by Canadian Tire, Noma, or Ayla Networks. Use at your own risk.
