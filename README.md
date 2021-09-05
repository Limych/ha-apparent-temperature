*Please :star: this repo if you find it useful*

# Sensor of Temperature Feels Like for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![Support me on Patreon][patreon-shield]][patreon]

[![Community Forum][forum-shield]][forum]

## Installation

### Install from HACS (recommended)

1. Have [HACS][hacs] installed, this will allow you to easily manage and track updates.
1. Search for "Temperature Feels Like".
1. Click Install below the found integration.

... then if you want to use `configuration.yaml` to configure sensor...
1. Add `temperature_feels_like` sensor to your `configuration.yaml` file. See configuration examples below.
1. Restart Home Assistant

### Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `temperature_feels_like`.
1. Download file `temperature_feels_like.zip` from the [latest release section][releases-latest] in this repository.
1. Extract _all_ files from this archive you downloaded in the directory (folder) you created.
1. Restart Home Assistant

... then if you want to use `configuration.yaml` to configure sensor...
1. Add `temperature_feels_like` sensor to your `configuration.yaml` file. See configuration examples below.
1. Restart Home Assistant

### Configuration Examples

#### Weather Entity Example

```yaml
# Example configuration.yaml entry
sensor:
  - platform: temperature_feels_like
    source: weather.home
```

#### Independent Temperature and Humidity Entities Example

```yaml
# Example configuration.yaml entry
sensor:
  - platform: temperature_feels_like
    name: 'Basement Feels Like Temperature'
    source:
      - sensor.basement_temperature
      - sensor.basement_humidity
```

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

### Configuration Variables

**source:**\
  _(string | list of strings) (Required)_\
  Weather provider entity ID or climate entity ID or list of sensors entity IDs.\
  For calculations sensor uses temperature, humidity and wind speed values. Temperature and humidity values is required. Wind speed value is optional.\
  Weather provider provide all values. Climate object provide only temperature and humidity.

> **_Note_**:\
> You can use groups of entities as a data source. These groups will be automatically expanded to individual entities.

> **_Note_**:\
> If you specify several sources of the same type of data (for example, a weather provider and a separate temperature sensor), the sensor uses only one of them as a source (the one that will be the last in the list). Therefore, the result of calculations can be unpredictable.

**name:**\
  _(string) (Optional) (Default value: name of first source + " Temperature Feels Like")_\
  Name to use in the frontend.

**unique_id**\
  _(string) (Optional)_\
  An ID that uniquely identifies this sensor. Set this to a unique value to allow customization through the UI.

## Track updates

You can automatically track new versions of this component and update it by [HACS][hacs].

## Troubleshooting

To enable debug logs use this configuration:
```yaml
# Example configuration.yaml entry
logger:
  default: info
  logs:
    custom_components.temperature_feels_like: debug
```
... then restart HA.

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this component is by [Andrey "Limych" Khrolenok](https://github.com/Limych).

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

***

[component]: https://github.com/Limych/ha-temperature-feeling
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-temperature-feeling.svg?style=popout
[commits]: https://github.com/Limych/ha-temperature-feeling/commits/master
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=popout
[hacs]: https://hacs.xyz
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/sensor-of-temperature-feels-like/299063
[license]: https://github.com/Limych/ha-temperature-feeling/blob/main/LICENSE.md
[license-shield]: https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout
[maintenance-shield]: https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout
[releases-shield]: https://img.shields.io/github/release/Limych/ha-temperature-feeling.svg?style=popout
[releases]: https://github.com/Limych/ha-temperature-feeling/releases
[releases-latest]: https://github.com/Limych/ha-temperature-feeling/releases/latest
[user_profile]: https://github.com/Limych
[report_bug]: https://github.com/Limych/ha-temperature-feeling/issues/new?template=bug_report.md
[suggest_idea]: https://github.com/Limych/ha-temperature-feeling/issues/new?template=feature_request.md
[contributors]: https://github.com/Limych/ha-temperature-feeling/graphs/contributors
[patreon-shield]: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3DLimych%26type%3Dpatrons&style=popout
[patreon]: https://www.patreon.com/join/limych
