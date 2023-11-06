"""Sensor platform for temperature_feels_like."""
from collections.abc import Callable
import logging
import math
from typing import List, Optional

import voluptuous as vol

from homeassistant.components.climate import (
    ATTR_CURRENT_HUMIDITY,
    ATTR_CURRENT_TEMPERATURE,
    DOMAIN as CLIMATE,
)
from homeassistant.components.group import expand_entity_ids
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.components.weather import (
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_WIND_SPEED,
    DOMAIN as WEATHER,
)
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_NAME,
    CONF_SOURCE,
    CONF_UNIQUE_ID,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    EVENT_HOMEASSISTANT_START,
    PERCENTAGE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, State, callback, split_entity_id
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.unit_conversion import TemperatureConverter
from homeassistant.util.unit_system import METRIC_SYSTEM, TEMPERATURE_UNITS

from .const import (
    ATTR_HUMIDITY_SOURCE,
    ATTR_HUMIDITY_SOURCE_VALUE,
    ATTR_TEMPERATURE_SOURCE,
    ATTR_TEMPERATURE_SOURCE_VALUE,
    ATTR_WIND_SPEED_SOURCE,
    ATTR_WIND_SPEED_SOURCE_VALUE,
    STARTUP_MESSAGE,
)

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SOURCE): cv.entity_ids,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
    }
)


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info=None,
):
    """Set up the Car Wash sensor."""
    # Print startup message
    _LOGGER.info(STARTUP_MESSAGE)

    async_add_entities(
        [
            TemperatureFeelingSensor(
                config.get(CONF_UNIQUE_ID),
                config.get(CONF_NAME),
                expand_entity_ids(hass, config.get(CONF_SOURCE)),
            )
        ]
    )


WIND_SPEED_UNITS = {
    UnitOfSpeed.METERS_PER_SECOND: 1,
    UnitOfSpeed.KILOMETERS_PER_HOUR: 3.6,
    UnitOfSpeed.MILES_PER_HOUR: 2.237,
}


class TemperatureFeelingSensor(SensorEntity):
    """temperature_feels_like Sensor class."""

    _attr_icon = "mdi:thermometer-lines"
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_state_class: SensorStateClass = SensorStateClass.MEASUREMENT
    _attr_should_poll: bool = False
    _attr_native_unit_of_measurement: str = UnitOfTemperature.CELSIUS

    def __init__(
        self, unique_id: Optional[str], name: Optional[str], sources: List[str]
    ):
        """Class initialization."""
        self._attr_unique_id = unique_id
        self._attr_native_value = None

        self._name = name
        self._sources = sources

        self._temp = None
        self._humd = None
        self._wind = None
        self._temp_val = None
        self._humd_val = None
        self._wind_val = None

    @property
    def name(self):
        """Return the name of the sensor."""
        if self._name:
            return self._name

        name = split_entity_id(self._sources[0])[1]
        if name.find("temperature") < 0:
            name += " Temperature"
        name += " Feels Like"
        return name

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return {
            ATTR_TEMPERATURE_SOURCE: self._temp,
            ATTR_TEMPERATURE_SOURCE_VALUE: self._temp_val,
            ATTR_HUMIDITY_SOURCE: self._humd,
            ATTR_HUMIDITY_SOURCE_VALUE: self._humd_val,
            ATTR_WIND_SPEED_SOURCE: self._wind,
            ATTR_WIND_SPEED_SOURCE_VALUE: self._wind_val,
        }

    async def async_added_to_hass(self):
        """Register callbacks."""

        # pylint: disable=unused-argument
        @callback
        def sensor_state_listener(entity, old_state, new_state):
            """Handle device state changes."""
            self.async_schedule_update_ha_state(True)

        # pylint: disable=unused-argument
        @callback
        def sensor_startup(event):
            """Update entity on startup."""
            entities = set()
            for entity_id in self._sources:
                state: State = self.hass.states.get(entity_id)
                domain = split_entity_id(state.entity_id)[0]
                device_class = state.attributes.get(ATTR_DEVICE_CLASS)
                unit_of_measurement = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)

                if (
                    device_class == DEVICE_CLASS_TEMPERATURE
                    or domain in (WEATHER, CLIMATE)
                    or unit_of_measurement in TEMPERATURE_UNITS
                    or entity_id.find("temperature") >= 0
                ):
                    self._temp = entity_id
                    entities.add(entity_id)

                if (
                    device_class == DEVICE_CLASS_HUMIDITY
                    or domain in (WEATHER, CLIMATE)
                    or unit_of_measurement == PERCENTAGE
                    or entity_id.find("humidity") >= 0
                ):
                    self._humd = entity_id
                    entities.add(entity_id)

                if (
                    domain == WEATHER
                    or unit_of_measurement in WIND_SPEED_UNITS
                    or entity_id.find("wind") >= 0
                ):
                    self._wind = entity_id
                    entities.add(entity_id)

            if not self._name:
                state: State = self.hass.states.get(self._temp)
                self._name = state.name
                if self._name.lower().find("temperature") < 0:
                    self._name += " Temperature"
                self._name += " Feels Like"

            async_track_state_change(self.hass, list(entities), sensor_state_listener)

            self.async_schedule_update_ha_state(True)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, sensor_startup)

    @staticmethod
    def _has_state(state) -> bool:
        """Return True if state has any value."""
        return state is not None and state not in [
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
            "None",
            "",
        ]

    def _get_temperature(self, entity_id: Optional[str]) -> Optional[float]:
        """Get temperature value (in °C) from entity."""
        if entity_id is None:
            return None
        state: State = self.hass.states.get(entity_id)
        if state is None:
            return None

        domain = split_entity_id(state.entity_id)[0]
        if domain == WEATHER:
            temperature = state.attributes.get(ATTR_WEATHER_TEMPERATURE)
            entity_unit = self.unit_of_measurement
        elif domain == CLIMATE:
            temperature = state.attributes.get(ATTR_CURRENT_TEMPERATURE)
            entity_unit = self.unit_of_measurement
        else:
            temperature = state.state
            entity_unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)

        if not self._has_state(temperature):
            return None

        try:
            temperature = TemperatureConverter.convert(
                float(temperature), entity_unit, UnitOfTemperature.CELSIUS
            )
        except ValueError as exc:
            _LOGGER.error('Could not convert value "%s" to float: %s', state, exc)
            return None

        return float(temperature)

    def _get_humidity(self, entity_id: Optional[str]) -> Optional[float]:
        """Get humidity value from entity."""
        if entity_id is None:
            return None
        state: State = self.hass.states.get(entity_id)
        if state is None:
            return None

        domain = split_entity_id(state.entity_id)[0]
        if domain == WEATHER:
            humidity = state.attributes.get(ATTR_WEATHER_HUMIDITY)
        elif domain == CLIMATE:
            humidity = state.attributes.get(ATTR_CURRENT_HUMIDITY)
        else:
            humidity = state.state

        if not self._has_state(humidity):
            return None

        return float(humidity)

    def _get_wind_speed(self, entity_id: Optional[str]) -> Optional[float]:
        """Get wind speed value from entity."""
        if entity_id is None:
            return 0.0
        state: State = self.hass.states.get(entity_id)
        if state is None:
            return 0.0

        domain = split_entity_id(state.entity_id)[0]
        if domain == WEATHER:
            wind_speed = state.attributes.get(ATTR_WEATHER_WIND_SPEED)
            entity_unit = (
                UnitOfSpeed.KILOMETERS_PER_HOUR
                if self.hass.config.units is METRIC_SYSTEM
                else UnitOfSpeed.MILES_PER_HOUR
            )
        else:
            wind_speed = state.state
            entity_unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)

        if not self._has_state(wind_speed):
            return None

        if entity_unit != UnitOfSpeed.METERS_PER_SECOND:
            wind_speed = float(wind_speed) / WIND_SPEED_UNITS[entity_unit]

        return float(wind_speed)

    async def async_update(self):
        """Update sensor state."""
        self._temp_val = temp = self._get_temperature(self._temp)  # °C
        self._humd_val = humd = self._get_humidity(self._humd)  # %
        self._wind_val = wind = self._get_wind_speed(self._wind)  # m/s

        _LOGGER.debug("Temp: %s °C  Hum: %s %%  Wind: %s m/s", temp, humd, wind)

        if temp is None or humd is None:
            _LOGGER.warning(
                "Can't calculate sensor value: some sources are unavailable."
            )
            self._attr_native_value = None
            return

        if wind is None:
            _LOGGER.warning(
                "Can't get wind speed value. Wind speed will be ignored in calculation."
            )
            wind = 0

        e_value = humd * 0.06105 * math.exp((17.27 * temp) / (237.7 + temp))
        self._attr_native_value = round(temp + 0.348 * e_value - 0.7 * wind - 4.25, 1)
        _LOGGER.debug(
            "New sensor state is %s %s",
            self._attr_native_value,
            self._attr_native_unit_of_measurement,
        )
