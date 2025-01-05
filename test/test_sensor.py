"""Test for the RTE Jours Signalés integration sensors."""

from unittest.mock import patch
import datetime
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.rte_jours_signales import async_setup_entry
from custom_components.rte_jours_signales.const import (
    DOMAIN,
    CONFIG_CLIEND_SECRET,
    CONFIG_CLIENT_ID,
    FRANCE_TZ,
)
from .const import MOCK_CLIENT_ID, MOCK_CLIENT_SECRET

async def test_sensors_unknown(
    anyio_backend,
    hass,
    mock_get_signal_days,
    mock_get_access_token,
    mock_update_signal_days,
):
    """Test basic sensor when no signal are found."""
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONFIG_CLIENT_ID: MOCK_CLIENT_ID, CONFIG_CLIEND_SECRET: MOCK_CLIENT_SECRET},
        options={},
        entry_id="mock",
    )
    config_entry.add_to_hass(hass)

    # setup the entry
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # current sensor should be created
    state_current = hass.states.get("sensor.rte_jours_signales_signal_current")
    assert state_current
    assert state_current.state == "unknown"

    # next sensor should be created
    state_next = hass.states.get("sensor.rte_jours_signales_signal_next")
    assert state_next
    assert state_next.state == "unknown"

@patch("custom_components.rte_jours_signales.sensor._current_datetime")
async def test_sensors(
    current_datetime,
    anyio_backend,
    hass,
    mock_get_signal_days,
    mock_get_access_token,
    mock_update_signal_days,
):
    """Test basic sensor when signal are found."""
    current_datetime.return_value = datetime.datetime(year=2025, month=1, day=1, hour=13, minute=37, second=0, tzinfo=FRANCE_TZ)
    
    # create a mock config entry to bypass the config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONFIG_CLIENT_ID: MOCK_CLIENT_ID, CONFIG_CLIEND_SECRET: MOCK_CLIENT_SECRET},
        options={},
        entry_id="mock",
    )
    config_entry.add_to_hass(hass)

    # setup the entry
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # current sensor should be created
    state_current = hass.states.get("sensor.rte_jours_signales_signal_current")
    assert state_current
    assert state_current.state == "explicit"

    # next sensor should be created
    state_next = hass.states.get("sensor.rte_jours_signales_signal_next")
    assert state_next
    assert state_next.state == "not_reported"
