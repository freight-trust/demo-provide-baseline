#!/usr/bin/env bash

# Allow for translating a env var into a local config file
if [[ -n "${JSON_CONFIG_FILE_VALUE}" ]]; then
    echo "Config file provided by env var. Writing to file..."
    echo $JSON_CONFIG_FILE_VALUE
    echo "${JSON_CONFIG_FILE_VALUE}" > /tmp/config.json
    export CONFIG_FILE=/tmp/config.json
fi
if [[ -n "${YAML_CONFIG_FILE_VALUE}" ]]; then
    echo "Config file provided by env var. Writing to file..."
    echo $YAML_CONFIG_FILE_VALUE
    echo "${YAML_CONFIG_FILE_VALUE}" > /tmp/config.yaml
    export CONFIG_FILE=/tmp/config.yaml
fi

set -euo pipefail

cd /contract-event-listener

case "${1,,}" in
  worker)
    make run
    ;;
  worker-debug)
    make run-debug
    ;;
  test)
    make test
    ;;
  container)
    echo "Container started"
    tail -f /dev/null
    ;;
  *)
    echo "No mode specified" && exit 1
esac
