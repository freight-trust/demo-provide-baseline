#!/usr/bin/env bash

set -euo pipefail
cd /system-tests
case "${1,,}" in
  test)
    pytest -xvv tests
    ;;
  container)
    echo "Container started"
    tail -f /dev/null
    ;;
  *)
    echo "No mode specified" && exit 1
esac
