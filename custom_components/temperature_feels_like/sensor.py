"""Sensor platform for temperature_feels_like."""
import logging
import math
from typing import Callable, List, Optional

import voluptuous as vol
from homeassistant.components.climate import (
    ATTR_CURRENT_HUMIDITY,
    ATTR_CURRENT_TEMPERATURE,
)
from homeassistant.components.climate import DOMAIN as CLIMATE
from homeassistant.components.history import LazyState
from homeassistant.components.weather import (
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_WIND_SPEED,
)
from homeassistant.components.weather import DOMAIN as WEATHER
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_NAME,
    CONF_SOURCE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    EVENT_HOMEASSISTANT_START,
    PERCENTAGE,
    SPEED_METERS_PER_SECOND,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant, callback, split_entity_id
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.temperature import convert as convert_temperature
from homeassistant.util.unit_system import TEMPERATURE_UNITS

from .const import STARTUP_MESSAGE

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SOURCE): cv.entity_ids,
        vol.Optional(CONF_NAME): cv.string,
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

    name = config.get(CONF_NAME)
    sources = config.get(CONF_SOURCE)

    async_add_entities([TemperatureFeelingSensor(hass, name, sources)])


class TemperatureFeelingSensor(Entity):
    """temperature_feels_like Sensor class."""

    def __init__(self, hass: HomeAssistant, name: Optional[str], sources: List[str]):
        """Class initialization."""
        self._hass = hass
        self._name = name
        self._sources = sources

        self._state = None
        self._temp = None
        self._humd = None
        self._wind = None

        self._unique_id = "{}-{}".format(split_entity_id(sources[0])[1], len(sources))

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self._unique_id

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return DEVICE_CLASS_TEMPERATURE

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement of this entity."""
        return self._hass.config.units.temperature_unit

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
            if not self._name:
                state = self._hass.states.get(self._sources[0])  # type: LazyState
                self._name = state.attributes["friendly_name"]
                if self._name.lower().find("temperature") < 0:
                    self._name += " Temperature"
                self._name += " Feels Like"

            entities = set()
            for entity_id in self._sources:
                state = self._hass.states.get(entity_id)  # type: LazyState
                domain = split_entity_id(state.entity_id)[0]
                device_class = state.attributes.get(ATTR_DEVICE_CLASS)
                unit_of_measurement = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)

                if (
                    device_class == DEVICE_CLASS_TEMPERATURE
                    or domain in (WEATHER, CLIMATE)
                    or unit_of_measurement in TEMPERATURE_UNITS
                ):
                    self._temp = entity_id
                    entities.add(entity_id)

                if (
                    device_class == DEVICE_CLASS_HUMIDITY
                    or domain in (WEATHER, CLIMATE)
                    or unit_of_measurement == PERCENTAGE
                ):
                    self._humd = entity_id
                    entities.add(entity_id)

                if domain == WEATHER or unit_of_measurement == SPEED_METERS_PER_SECOND:
                    self._wind = entity_id
                    entities.add(entity_id)

            async_track_state_change(self._hass, list(entities), sensor_state_listener)

            self.async_schedule_update_ha_state(True)

        self._hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, sensor_startup)

    @staticmethod
    def _has_state(state) -> bool:
        """Return True if state has any value."""
        return state is not None and state not in [
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
            "None",
            "",
        ]

    def _get_temperature(self, entity_id: str) -> Optional[float]:
        """Get temperature value (in °C) from entity."""
        state = self._hass.states.get(entity_id)  # type: LazyState
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
            temperature = convert_temperature(
                float(temperature), entity_unit, TEMP_CELSIUS
            )
        except ValueError as exc:
            _LOGGER.error('Could not convert value "%s" to float: %s', state, exc)
            return None

        return float(temperature)

    def _get_humidity(self, entity_id: Optional[str]) -> Optional[float]:
        """Get humidity value from entity."""
        if entity_id is None:
            return 0.0
        state = self._hass.states.get(entity_id)  # type: LazyState
        if state is None:
            return 0.0

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
        state = self._hass.states.get(entity_id)  # type: LazyState
        if state is None:
            return 0.0

        domain = split_entity_id(state.entity_id)[0]
        if domain == WEATHER:
            wind_speed = state.attributes.get(ATTR_WEATHER_WIND_SPEED)
        else:
            wind_speed = state.state

        if not self._has_state(wind_speed):
            return None

        return float(wind_speed)

    async def async_update(self):
        """Update sensor state."""
        temp = self._get_temperature(self._temp)  # °C
        humd = self._get_humidity(self._humd)
        wind = self._get_wind_speed(self._wind)

        _LOGGER.debug("Temp: %s °C  Hum: %s %%  Wind: %s m/s", temp, humd, wind)

        if temp is None or humd is None or wind is None:
            _LOGGER.warning(
                "Can't calculate sensor value: some sources are unavailable."
            )
            self._state = None
            return

        e_value = humd * 0.06105 * math.exp((17.27 * temp) / (237.7 + temp))
        feeling = temp + 0.348 * e_value - 0.7 * wind - 4.25
        self._state = round(
            convert_temperature(feeling, TEMP_CELSIUS, self.unit_of_measurement), 1
        )
        _LOGGER.debug(
            "New sensor state is %s %s", self._state, self.unit_of_measurement
        )
