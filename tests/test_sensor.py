# pylint: disable=protected-access,redefined-outer-name
"""The test for the sensor platform."""
from homeassistant.components.weather import (
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_WIND_SPEED,
)
from homeassistant.const import CONF_PLATFORM, CONF_SOURCE, DEVICE_CLASS_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import assert_setup_component

from custom_components.temperature_feels_like.const import DOMAIN
from custom_components.temperature_feels_like.sensor import TemperatureFeelingSensor

TEST_CONFIG = {
    CONF_PLATFORM: DOMAIN,
    CONF_SOURCE: "weather.test_monitored",
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
                "humidity_template": "{{ 32 }}",
                "wind_speed_template": "{{ 2 }}",
            }
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
                                "unit_of_measurement": "°C",
                                "value_template": "{{ 20 }}",
                                "device_class": "temperature",
                            },
                            "test_humidity": {
                                "unit_of_measurement": "%",
                                "value_template": "{{ 40 }}",
                                "device_class": "humidity",
                            },
                            "test_wind_speed": {
                                "unit_of_measurement": "m/s",
                                "value_template": "{{ 10 }}",
                            },
                        },
                    },
                ],
            },
        )
    await hass.async_block_till_done()


async def test_entity_initialization(hass: HomeAssistant):
    """Test sensor initialization."""
    entity = TemperatureFeelingSensor(hass, "test", ["weather.test_monitored"])

    assert entity.unique_id == "test_monitored-1"
    assert entity.name == "test"
    assert entity.device_class == DEVICE_CLASS_TEMPERATURE
    assert entity.should_poll is False
    assert entity.available is True
    assert entity.state is None


async def test_async_setup_platform(hass: HomeAssistant):
    """Test platform setup."""
    await async_setup_test_entities(hass)

    await hass.async_start()
    await hass.async_block_till_done()

    state = hass.states.get("sensor.temperature_feels_like_test_monitored_1")
    assert (
        state.attributes.get("friendly_name") == "test_monitored Temperature Feels Like"
    )
    assert state is not None
    assert state.state == "7.9"

    hass.states.async_set(
        "weather.test_monitored",
        "0",
        {
            ATTR_WEATHER_TEMPERATURE: 20,
            ATTR_WEATHER_HUMIDITY: 0,
            ATTR_WEATHER_WIND_SPEED: 0,
        },
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.temperature_feels_like_test_monitored_1")
    assert state is not None
    assert state.state == "15.8"

    hass.states.async_set(
        "weather.test_monitored",
        "0",
        {
            ATTR_WEATHER_TEMPERATURE: 0,
            ATTR_WEATHER_HUMIDITY: 20,
            ATTR_WEATHER_WIND_SPEED: 0,
        },
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.temperature_feels_like_test_monitored_1")
    assert state is not None
    assert state.state == "-3.8"

    hass.states.async_set(
        "weather.test_monitored",
        "0",
        {
            ATTR_WEATHER_TEMPERATURE: 0,
            ATTR_WEATHER_HUMIDITY: 0,
            ATTR_WEATHER_WIND_SPEED: 20,
        },
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.temperature_feels_like_test_monitored_1")
    assert state is not None
    assert state.state == "-18.2"


async def test__get_temperature(hass: HomeAssistant):
    """Test temperature getter."""
    await async_setup_test_entities(hass)

    entity = TemperatureFeelingSensor(hass, "test", ["weather.test_monitored"])

    assert entity._get_temperature("sensor.unexistent") is None
    assert entity._get_temperature("weather.test_monitored") == 12.0
    assert entity._get_temperature("sensor.test_temperature") == 20.0


async def test__get_humidity(hass: HomeAssistant):
    """Test humidity getter."""
    await async_setup_test_entities(hass)

    entity = TemperatureFeelingSensor(hass, "test", ["weather.test_monitored"])

    assert entity._get_humidity(None) == 0.0
    assert entity._get_humidity("sensor.unexistent") == 0.0
    assert entity._get_humidity("weather.test_monitored") == 32.0
    assert entity._get_humidity("sensor.test_humidity") == 40.0


async def test__get_wind_speed(hass: HomeAssistant):
    """Test wind speed getter."""
    await async_setup_test_entities(hass)

    entity = TemperatureFeelingSensor(hass, "test", ["weather.test_monitored"])

    assert entity._get_wind_speed(None) == 0.0
    assert entity._get_wind_speed("sensor.unexistent") == 0.0
    assert entity._get_wind_speed("weather.test_monitored") == 2.0
    assert entity._get_wind_speed("sensor.test_wind_speed") == 10.0


async def test_async_update(hass: HomeAssistant):
    """Test platform setup."""
    await async_setup_test_entities(hass)

    entity = TemperatureFeelingSensor(hass, "test", ["weather.nonexistent"])

    entity._temp = "weather.nonexistent"
    await entity.async_update()
    assert entity.state is None

    entity._temp = "weather.test_monitored"
    await entity.async_update()
    assert entity.state is not None
    assert entity.state == 7.8
