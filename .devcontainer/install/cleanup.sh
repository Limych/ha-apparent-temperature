#!/usr/bin/env bash

echo -e "\\033[0;34mRunning cleanup script 'cleanup.sh'\\033[0m"

rm -fr /var/lib/apt/lists/*
rm -fr /tmp/* /var/{cache,log}/*

rm -fr /container
rm -fr /install
