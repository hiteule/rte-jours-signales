"""Configure pytest for all tests."""

from unittest.mock import patch

import pytest

from .const import MOCK_SIGNAL_DAY

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture()
def hass(hass, enable_custom_integrations):
    """Return a Home Assistant instance that can load custom integrations."""
    yield hass


@pytest.fixture()
def anyio_backend():
    """Define the 'anyio_backend' fixture for asyncio.

    see https://anyio.readthedocs.io/en/stable/testing.html
    """
    return "asyncio"


@pytest.fixture()
def bypass_integration_setup():
    """Fixture to replace 'async_setup_entry' with a mock."""
    with (
        patch("custom_components.rte_jours_signales.async_setup_entry", return_value=True),
        patch(
            "custom_components.rte_jours_signales.async_unload_entry", return_value=True
        ) as mock,
    ):
        yield mock


@pytest.fixture()
def mock_get_signal_days():
    """Fixture to replace 'APIWorker.get_signal_days' method with a mock."""
    with patch(
        "custom_components.rte_jours_signales.api_worker.APIWorker.get_signal_days",
        return_value=MOCK_SIGNAL_DAY,
    ) as mock:
        yield mock

@pytest.fixture()
def mock_application_tester():
    """Fixture to replace 'application_tester' method with a mock."""
    with patch(
        "custom_components.rte_jours_signales.api_worker.application_tester",
        return_value=None,
    ) as mock:
        yield mock

@pytest.fixture()
def mock_get_access_token():
    """Fixture to replace 'APIWorker.get_signal_days' method with a mock."""
    with patch(
        "custom_components.rte_jours_signales.api_worker.APIWorker._get_access_token",
        return_value=None,
    ) as mock:
        yield mock

@pytest.fixture()
def mock_update_signal_days():
    """Fixture to replace 'APIWorker.get_signal_days' method with a mock."""
    with patch(
        "custom_components.rte_jours_signales.api_worker.APIWorker._update_signal_days",
        return_value=None,
    ) as mock:
        yield mock
