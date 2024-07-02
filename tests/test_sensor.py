# pylint: disable=protected-access,redefined-outer-name
"""The test for the sensor platform."""
from typing import Final

import pytest
from pytest_homeassistant_custom_component.common import assert_setup_component

from custom_components.apparent_temperature.const import (
    ATTR_HUMIDITY_SOURCE,
    ATTR_HUMIDITY_SOURCE_VALUE,
    ATTR_TEMPERATURE_SOURCE,
    ATTR_TEMPERATURE_SOURCE_VALUE,
    ATTR_WIND_SPEED_SOURCE,
    ATTR_WIND_SPEED_SOURCE_VALUE,
    DOMAIN,
)
from custom_components.apparent_temperature.sensor import ApparentTemperatureSensor
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorStateClass
from homeassistant.components.weather import (
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_TEMPERATURE_UNIT,
    ATTR_WEATHER_WIND_SPEED,
    ATTR_WEATHER_WIND_SPEED_UNIT,
)
from homeassistant.const import (
    CONF_PLATFORM,
    CONF_SOURCE,
    PERCENTAGE,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

TEST_UNIQUE_ID: Final = "test_id"
TEST_NAME: Final = "test_name"
TEST_SOURCES: Final = ["group.test_group"]

TEST_CONFIG: Final = {
    CONF_PLATFORM: DOMAIN,
    CONF_SOURCE: TEST_SOURCES,
}


async def async_setup_test_entities(hass: HomeAssistant):
    """Mock weather entity."""
    assert await async_setup_component(
        hass,
        "weather",
        {
            "weather": {
                "platform": "template",
                "name": "test_monitored",
                "condition_template": "{{ 0 }}",
                "temperature_template": "{{ 12 }}",
                ATTR_WEATHER_TEMPERATURE_UNIT: UnitOfTemperature.CELSIUS,
                "humidity_template": "{{ 32 }}",
                "wind_speed_template": "{{ 10 }}",
                ATTR_WEATHER_WIND_SPEED_UNIT: UnitOfSpeed.KILOMETERS_PER_HOUR,
            }
        },
    )
    await hass.async_block_till_done()

    assert await async_setup_component(
        hass,
        "group",
        {
            "group": {
                "test_group": {
                    "entities": [
                        "sensor.test_temperature",
                        "sensor.test_temperature_f",
                        "sensor.test_humidity",
                        "sensor.test_wind_speed",
                        "weather.test_monitored",
                    ],
                },
            },
        },
    )
    await hass.async_block_till_done()

    with assert_setup_component(2, "sensor"):
        assert await async_setup_component(
            hass,
            "sensor",
            {
                "sensor": [
                    TEST_CONFIG,
                    {
                        CONF_PLATFORM: "template",
                        "sensors": {
                            "test_temperature": {
                                "unit_of_measurement": UnitOfTemperature.CELSIUS,
                                "value_template": "{{ 20 }}",
                                "device_class": "temperature",
                            },
                            "test_temperature_f": {
                                "unit_of_measurement": UnitOfTemperature.FAHRENHEIT,
                                "value_template": "{{ 20 }}",
                                "device_class": "temperature",
                            },
                            "test_humidity": {
                                "unit_of_measurement": PERCENTAGE,
                                "value_template": "{{ 40 }}",
                                "device_class": "humidity",
                            },
                            "test_wind_speed": {
                                "unit_of_measurement": UnitOfSpeed.METERS_PER_SECOND,
                                "value_template": "{{ 10 }}",
                            },
                            "test_wind_speed_kmh": {
                                "unit_of_measurement": UnitOfSpeed.KILOMETERS_PER_HOUR,
                                "value_template": "{{ 10 }}",
                            },
                            "test_wind_speed_mph": {
                                "unit_of_measurement": UnitOfSpeed.MILES_PER_HOUR,
                                "value_template": "{{ 10 }}",
                            },
                            "test_unavailable": {
                                "value_template": "{{ 10 }}",
                                "availability_template": "{{ False }}",
                            },
                        },
                    },
                ],
            },
        )
    await hass.async_block_till_done()


async def test_entity_initialization(hass: HomeAssistant):
    """Test sensor initialization."""
    entity = ApparentTemperatureSensor(None, TEST_NAME, TEST_SOURCES)

    assert entity.unique_id is None

    entity = ApparentTemperatureSensor(TEST_UNIQUE_ID, TEST_NAME, TEST_SOURCES)

    entity.hass = hass

    assert entity.unique_id == TEST_UNIQUE_ID
    assert entity.name == TEST_NAME
    assert entity.device_class == NumberDeviceClass.TEMPERATURE
    assert entity.state_class == SensorStateClass.MEASUREMENT
    assert entity.should_poll is False
    assert entity.available is True
    assert entity.state is None
    assert entity.extra_state_attributes == {
        ATTR_TEMPERATURE_SOURCE: None,
        ATTR_TEMPERATURE_SOURCE_VALUE: None,
        ATTR_HUMIDITY_SOURCE: None,
        ATTR_HUMIDITY_SOURCE_VALUE: None,
        ATTR_WIND_SPEED_SOURCE: None,
        ATTR_WIND_SPEED_SOURCE_VALUE: None,
    }

    entity = ApparentTemperatureSensor(
        TEST_UNIQUE_ID, None, ["sensors.test_temperature"]
    )

    assert entity.name == "test_Apparent temperature"

    entity = ApparentTemperatureSensor(TEST_UNIQUE_ID, None, ["sensors.test_humidity"])

    assert entity.name == "test_humidity Apparent Temperature"


@pytest.mark.parametrize(
    "temp, humi, wind, expected",
    [
        (12, 32, 10, "7.365"),
        (20, 0, 0, "15.75"),
        (0, 20, 0, "-3.825"),
        (0, 0, 20, "-8.139"),
    ],
)
async def test_async_setup_platform(hass: HomeAssistant, temp, humi, wind, expected):
    """Test platform setup."""
    await async_setup_test_entities(hass)

    await hass.async_start()
    await hass.async_block_till_done()

    hass.states.async_set(
        "weather.test_monitored",
        "0",
        {
            ATTR_WEATHER_TEMPERATURE: temp,
            ATTR_WEATHER_TEMPERATURE_UNIT: UnitOfTemperature.CELSIUS,
            ATTR_WEATHER_HUMIDITY: humi,
            ATTR_WEATHER_WIND_SPEED: wind,
            ATTR_WEATHER_WIND_SPEED_UNIT: UnitOfSpeed.KILOMETERS_PER_HOUR,
        },
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.test_apparent_temperature")
    assert state.attributes.get("friendly_name") == "test_Apparent temperature"
    assert state is not None
    assert state.state == expected
    assert state.attributes[ATTR_TEMPERATURE_SOURCE] == "weather.test_monitored"
    assert state.attributes[ATTR_HUMIDITY_SOURCE] == "weather.test_monitored"
    assert state.attributes[ATTR_WIND_SPEED_SOURCE] == "weather.test_monitored"
    assert state.attributes[ATTR_TEMPERATURE_SOURCE_VALUE] == temp
    assert state.attributes[ATTR_HUMIDITY_SOURCE_VALUE] == humi
    assert state.attributes[ATTR_WIND_SPEED_SOURCE_VALUE] == pytest.approx(
        wind / 3.6, 0.01
    )


async def test__get_temperature(hass: HomeAssistant):
    """Test temperature getter."""
    await async_setup_test_entities(hass)

    entity = ApparentTemperatureSensor(TEST_UNIQUE_ID, TEST_NAME, TEST_SOURCES)
    entity.hass = hass

    assert entity._get_temperature(None) is None
    assert entity._get_temperature("sensor.unexistent") is None
    assert entity._get_temperature("weather.test_monitored") == 12.0
    assert entity._get_temperature("sensor.test_temperature") == 20.0
    assert entity._get_temperature("sensor.test_temperature_f") == -7.0


async def test__get_humidity(hass: HomeAssistant):
    """Test humidity getter."""
    await async_setup_test_entities(hass)

    entity = ApparentTemperatureSensor(TEST_UNIQUE_ID, TEST_NAME, TEST_SOURCES)
    entity.hass = hass

    assert entity._get_humidity(None) is None
    assert entity._get_humidity("sensor.unexistent") is None
    assert entity._get_humidity("weather.test_monitored") == 32.0
    assert entity._get_humidity("sensor.test_humidity") == 40.0


async def test__get_wind_speed(hass: HomeAssistant):
    """Test wind speed getter."""
    await async_setup_test_entities(hass)

    entity = ApparentTemperatureSensor(TEST_UNIQUE_ID, TEST_NAME, TEST_SOURCES)
    entity.hass = hass

    assert entity._get_wind_speed(None) == 0.0
    assert entity._get_wind_speed("sensor.unexistent") == 0.0
    assert entity._get_wind_speed("sensor.test_unavailable") is None
    assert entity._get_wind_speed("weather.test_monitored") == pytest.approx(2.77, 0.01)
    assert entity._get_wind_speed("sensor.test_wind_speed") == 10.0
    assert entity._get_wind_speed("sensor.test_wind_speed_kmh") == pytest.approx(
        2.77, 0.01
    )
    assert entity._get_wind_speed("sensor.test_wind_speed_mph") == pytest.approx(
        4.47, 0.01
    )


async def test_async_update(hass: HomeAssistant):
    """Test platform setup."""
    await async_setup_test_entities(hass)

    entity = ApparentTemperatureSensor(
        TEST_UNIQUE_ID, TEST_NAME, ["weather.nonexistent"]
    )
    entity.hass = hass

    entity._temp = "weather.nonexistent"
    entity._humd = "weather.test_monitored"
    await entity.async_update()
    assert entity.state is None

    entity._temp = "weather.test_monitored"
    entity._humd = "weather.nonexistent"
    await entity.async_update()
    assert entity.state is None

    entity._temp = "weather.test_monitored"
    entity._humd = "weather.test_monitored"
    await entity.async_update()
    assert entity.state is not None
    assert entity.state == 9.309

    entity._temp = "weather.test_monitored"
    entity._humd = "weather.test_monitored"
    entity._wind = "sensor.test_unavailable"
    await entity.async_update()
    assert entity.state is not None
    assert entity.state == 9.309

    entity._temp = "weather.test_monitored"
    entity._humd = "weather.test_monitored"
    entity._wind = "weather.test_monitored"
    await entity.async_update()
    assert entity.state is not None
    assert entity.state == 7.365
