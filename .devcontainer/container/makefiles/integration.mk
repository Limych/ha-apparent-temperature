start:  ## Start Home Assistant with the integration loaded
	@bash /opt/container/helpers/homeassistant/start.sh

run:
	start

up:
	start

set-version: ## Set Home Assistant version
	@bash /opt/container/helpers/homeassistant/set-version.sh

upgrade:  ## Upgrade Home Assistant to latest dev in the container
	@python3 -m pip --disable-pip-version-check install --upgrade git+https://github.com/home-assistant/home-assistant.git@dev

install:  ## Install Home Assistant dev in the container
	upgrade

check-config: ## Check Home Assistant config
	@hass -c /config --script check_config
