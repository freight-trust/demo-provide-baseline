#!/usr/bin/env bash

set -euo pipefail

cd /channel-api

case "${1,,}" in
  server)
    make run-api
    ;;
  callback-server)
    make run-callback-server
    ;;
  new-messages-observer-processor)
    make run-new-messages-observer-processor
    ;;
  callback-spreader-processor)
    make run-callback-spreader-processor
    ;;
  callback-delivery-processor)
    make run-callback-delivery-processor
    ;;
  test)
    make run-api &
    make test
    ;;
  container)
    echo "Container started"
    tail -f /dev/null
    ;;
  *)
    echo "No mode specified" && exit 1
esac
