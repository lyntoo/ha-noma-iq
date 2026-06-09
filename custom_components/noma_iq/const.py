"""Constants for Noma iQ integration."""

DOMAIN = "noma_iq"

AYLA_USER_URL = "https://user-field.aylanetworks.com"
AYLA_ADS_URL = "https://ads-field.aylanetworks.com"

CONF_APP_ID = "app_id"
CONF_APP_SECRET = "app_secret"

AC_OEM_MODELS = {"win-ac", "port-ac", "port8k-ac", "port10k-ac"}

PROP_POWER = "power"
PROP_MODE = "mode"
PROP_MODE_STATUS = "mode_status"
PROP_TARGET_TEMP = "target_temp"
PROP_AMBIENT_TEMP = "ambient_temp"
PROP_FAN_SPEED = "fan_speed"
PROP_FAN_SPEED_STATUS = "fan_speed_status"
PROP_SWING = "swing"
PROP_TEMP_UNIT = "temp_unit"
PROP_NIGHT_MODE = "nightMode_prop"

MODE_COOL = "Cool"
MODE_DRY = "Dry"
MODE_FAN = "Fan"

FAN_LOW = "Low"
FAN_MED = "Med"
FAN_HIGH = "High"
FAN_AUTO = "Auto"

POLL_INTERVAL = 30
