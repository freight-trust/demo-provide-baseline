#!/usr/bin/env bash

source /deployer/scripts/base.sh

(cd $CONTRACT_DEPLOYMENT_DIR && truffle exec "$@" --network production | pino-pretty)
