#!/usr/bin/env bash
set -e
echo -e "\\033[0;34mRunning install script 'container.sh'\\033[0m"

export DEBIAN_FRONTEND=noninteractive

apk add --no-cache \
    make \
    git

mkdir -p /opt/container/makefiles
mkdir -p /opt/container/helpers

cp /container/container.mk /opt/container/container.mk
cp -r /container/helpers /opt/container/

cp /container/container /usr/bin/container
chmod +x /usr/bin/container

cp /container/makefiles/integration.mk /opt/container/makefiles/integration.mk

container help
