"""Sensors for RTE Jours Signalés integration."""
from __future__ import annotations

import asyncio
import datetime
import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api_worker import APIWorker
from .const import (
    API_ATTRIBUTION,
    API_REQ_TIMEOUT,
    API_VALUE_SIGNAL_NOT_REPORTED,
    API_VALUE_SIGNAL_EXPLICIT,
    API_VALUE_SIGNAL_IMPLICIT,
    API_VALUE_SIGNAL_EXPLICIT_IMPLICIT,
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
    DEVICE_NAME,
    DOMAIN,
    FRANCE_TZ,
    SENSOR_SIGNAL_NOT_REPORTED_NAME,
    SENSOR_SIGNAL_EXPLICIT_NAME,
    SENSOR_SIGNAL_IMPLICIT_NAME,
    SENSOR_SIGNAL_EXPLICIT_IMPLICIT_NAME,
    SENSOR_SIGNAL_UNKNOWN_NAME,
)

_LOGGER = logging.getLogger(__name__)


# config flow setup
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Modern (thru config entry) sensors setup."""
    _LOGGER.debug("%s: setting up sensor plateform", config_entry.title)
    # Retrieve the API Worker object
    try:
        api_worker = hass.data[DOMAIN][config_entry.entry_id]
    except KeyError:
        _LOGGER.error(
            "%s: can not calendar: failed to get the API worker object",
            config_entry.title,
        )
        return
    # Wait request timeout to let API worker get first batch of data before initializing sensors
    await asyncio.sleep(API_REQ_TIMEOUT)
    # Init sensors
    sensors = [
        CurrentSignal(config_entry.entry_id, api_worker),
        NextSignal(config_entry.entry_id, api_worker),
    ]
    # Add the entities to HA
    async_add_entities(sensors, True)


class CurrentSignal(SensorEntity):
    """Current Signal Sensor Entity."""

    # Generic properties
    _attr_has_entity_name = True
    _attr_attribution = API_ATTRIBUTION
    # Sensor properties
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:transmission-tower"

    def __init__(self, config_id: str, api_worker: APIWorker) -> None:
        """Initialize the Current Signal Sensor."""

        self.entity_id = f"sensor.{DOMAIN}_signal_current"
        self._attr_unique_id = f"{DOMAIN}_{config_id}_signal_current"
        self._attr_translation_key = "signal_current"
        self._attr_options = [
            SENSOR_SIGNAL_NOT_REPORTED_NAME,
            SENSOR_SIGNAL_EXPLICIT_NAME,
            SENSOR_SIGNAL_IMPLICIT_NAME,
            SENSOR_SIGNAL_EXPLICIT_IMPLICIT_NAME,
            SENSOR_SIGNAL_UNKNOWN_NAME,
        ]
        self._attr_native_value: str | None = None
        self._config_id = config_id
        self._api_worker = api_worker

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._config_id)},
            name=DEVICE_NAME,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
        )

    @callback
    def update(self) -> None:
        """Update the value of the sensor from the thread object memory cache."""
        self._attr_available = True
        localized_now = _current_datetime()
        for signal_day in self._api_worker.get_signal_days():
            if signal_day.Start <= localized_now < signal_day.End:
                # Found a match !
                self._attr_native_value = get_signal_name(signal_day.Value)
                return
        # Nothing found
        _LOGGER.debug("Current signal is not available at this time (%s)", localized_now)
        self._attr_native_value = SENSOR_SIGNAL_UNKNOWN_NAME


class NextSignal(SensorEntity):
    """Next Signal Sensor Entity."""

    # Generic properties
    _attr_has_entity_name = True
    _attr_attribution = API_ATTRIBUTION
    # Sensor properties
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:transmission-tower-export"

    def __init__(self, config_id: str, api_worker: APIWorker) -> None:
        """Initialize the Next Signal Sensor."""

        self.entity_id = f"sensor.{DOMAIN}_signal_next"
        self._attr_unique_id = f"{DOMAIN}_{config_id}_signal_next"
        self._attr_translation_key = "signal_next"
        self._attr_options = [
            SENSOR_SIGNAL_NOT_REPORTED_NAME,
            SENSOR_SIGNAL_EXPLICIT_NAME,
            SENSOR_SIGNAL_IMPLICIT_NAME,
            SENSOR_SIGNAL_EXPLICIT_IMPLICIT_NAME,
            SENSOR_SIGNAL_UNKNOWN_NAME,
        ]
        self._attr_native_value: str | None = None
        self._config_id = config_id
        self._api_worker = api_worker

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._config_id)},
            name=DEVICE_NAME,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
        )

    @callback
    def update(self) -> None:
        """Update the value of the sensor from the thread object memory cache."""
        self._attr_available = True
        localized_now = _current_datetime()
        for signal_day in self._api_worker.get_signal_days():
            if localized_now < signal_day.Start:
                # Found a match !
                self._attr_native_value = get_signal_name(signal_day.Value)
                return
        _LOGGER.debug("Next signal is not available at this time (%s)", localized_now)
        self._attr_native_value = SENSOR_SIGNAL_UNKNOWN_NAME

def _current_datetime() -> datetime:
    """Return the current datetime"""
    return datetime.datetime.now(FRANCE_TZ)

def get_signal_name(value: str) -> str:
    """Return the corresponding name for a signal."""
    if value == API_VALUE_SIGNAL_NOT_REPORTED:
        return SENSOR_SIGNAL_NOT_REPORTED_NAME
    if value == API_VALUE_SIGNAL_EXPLICIT:
        return SENSOR_SIGNAL_EXPLICIT_NAME
    if value == API_VALUE_SIGNAL_IMPLICIT:
        return SENSOR_SIGNAL_IMPLICIT_NAME
    if value == API_VALUE_SIGNAL_EXPLICIT_IMPLICIT:
        return SENSOR_SIGNAL_EXPLICIT_IMPLICIT_NAME
    _LOGGER.warning("Can not get signal name for unknown value: %s", value)
    return SENSOR_SIGNAL_UNKNOWN_NAME
