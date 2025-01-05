"""Constants for the RTE Jours Signalés integration."""
from zoneinfo import ZoneInfo

DOMAIN = "rte_jours_signales"

# Config Flow
CONFIG_CLIENT_ID = "client_id"
CONFIG_CLIEND_SECRET = "client_secret"

# Service Device
DEVICE_NAME = "RTE Jours Signalés"
DEVICE_MANUFACTURER = "RTE"
DEVICE_MODEL = "Demand Response Signal"

# Sensors
SENSOR_SIGNAL_NOT_REPORTED_NAME = "not_reported"
SENSOR_SIGNAL_EXPLICIT_NAME = "explicit"
SENSOR_SIGNAL_IMPLICIT_NAME = "implicit"
SENSOR_SIGNAL_EXPLICIT_IMPLICIT_NAME = "explicit_implicit"
SENSOR_SIGNAL_UNKNOWN_NAME = "unknown"

# API
FRANCE_TZ = ZoneInfo("Europe/Paris")
API_DOMAIN = "digital.iservices.rte-france.com"
API_TOKEN_ENDPOINT = f"https://{API_DOMAIN}/token/oauth"
API_DEMAND_RESPONSE_SIGNAL_ENDPOINT = f"https://{API_DOMAIN}/open_api/demand_response_signal/v2/signals"
API_REQ_TIMEOUT = 3
API_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
API_KEY_ERROR = "error"
API_KEY_ERROR_DESC = "error_description"
API_KEY_START = "start_date"
API_KEY_END = "end_date"
API_KEY_VALUE = "aoe_signals"
API_KEY_UPDATED = "updated_date"
API_VALUE_SIGNAL_NOT_REPORTED = 0
API_VALUE_SIGNAL_EXPLICIT = 1
API_VALUE_SIGNAL_IMPLICIT = 2
API_VALUE_SIGNAL_EXPLICIT_IMPLICIT = 3

API_ATTRIBUTION = "Données fournies par data.rte-france.com"
USER_AGENT = "github.com/hiteule/rte-jours-signales v1.0.0"

# Demand Response Signal def
CONFIRM_HOUR = 10
CONFIRM_MIN = 45
