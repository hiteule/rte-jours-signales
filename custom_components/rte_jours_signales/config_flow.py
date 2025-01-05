"""Config flow for RTE Jours Signalés integration."""
from __future__ import annotations

import logging
from typing import Any

from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from requests.exceptions import RequestException
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .api_worker import BadRequest, ServerError, UnexpectedError, application_tester
from .const import CONFIG_CLIEND_SECRET, CONFIG_CLIENT_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONFIG_CLIENT_ID): str,
        vol.Required(CONFIG_CLIEND_SECRET): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RTE Jours Signalés integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # No input
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )
        # Validate input
        await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONFIG_CLIENT_ID]}")
        self._abort_if_unique_id_configured()
        errors = {}
        try:
            client_id = user_input[CONFIG_CLIENT_ID]
            client_secret = user_input[CONFIG_CLIEND_SECRET]
            await self.hass.async_add_executor_job(
                lambda: application_tester(str(client_id), str(client_secret))
            )
        except RequestException as request_exception:
            _LOGGER.error(
                "Application validation failed: network error: %s", request_exception
            )
            errors["base"] = "network_error"
        except OAuth2Error as oauth_error:
            _LOGGER.error("Application validation failed: oauth error: %s", oauth_error)
            errors["base"] = "oauth_error"
        except BadRequest as http_error:
            _LOGGER.error(
                "Application validation failed: bad request error: %s", http_error
            )
            errors["base"] = "http_client_error"
        except ServerError as http_error:
            _LOGGER.error("Application validation failed: server error: %s", http_error)
            errors["base"] = "http_server_error"
        except UnexpectedError as http_error:
            _LOGGER.error(
                "Application validation failed: unexpected error: %s", http_error
            )
            errors["base"] = "http_unexpected_error"
        else:
            return self.async_create_entry(
                title="Client ID: "+user_input[CONFIG_CLIENT_ID], data=user_input
            )
        # Show errors
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
