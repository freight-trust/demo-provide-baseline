#!/usr/bin/env bash

set -euo pipefail

export NODE_PATH="$(npm root -g --quiet)"
DEPLOYER_DIR=/deployer
DEPLOYER_SCRIPTS_DIR=$DEPLOYER_DIR/scripts
CONTRACT_DEPLOYMENT_DIR=/tmp/contract-deployment
CONTRACT_DIR="${CONTRACT_DIR:-/tmp/contract}"

cd $DEPLOYER_DIR
rsync -av $CONTRACT_DIR/ $CONTRACT_DEPLOYMENT_DIR/
rsync -av $DEPLOYER_SCRIPTS_DIR/truffle-config.js $CONTRACT_DEPLOYMENT_DIR/truffle-config.js
