"""Test for the RTE Jours Signalés integration config flow."""

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from custom_components.rte_jours_signales.const import (
    DOMAIN,
    CONFIG_CLIEND_SECRET,
    CONFIG_CLIENT_ID
)
from .const import MOCK_CLIENT_ID, MOCK_CLIENT_SECRET

async def test_config_flow_user_step_ok(
    anyio_backend, hass, bypass_integration_setup, mock_application_tester
):
    """Test that the 'user' config step correctly creates a config entry."""

    # Init the config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    # Check that the first step is a 'form'
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # If a user were to enter their client id and secret and submit the form it would result in this call.
    # Behind the scenes, the credentials are tested and the config entry is created.
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONFIG_CLIENT_ID: MOCK_CLIENT_ID, CONFIG_CLIEND_SECRET: MOCK_CLIENT_SECRET},
    )

    # To test the credentials, the application_tester method should be called
    mock_application_tester.assert_called_once()

    # a new config entry should be created
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == f"Client ID: {MOCK_CLIENT_ID}"
    assert result["data"] == {CONFIG_CLIENT_ID: MOCK_CLIENT_ID, CONFIG_CLIEND_SECRET: MOCK_CLIENT_SECRET}
    assert result["options"] == {}
    assert result["result"]
