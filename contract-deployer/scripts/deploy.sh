#!/usr/bin/env bash

source /deployer/scripts/base.sh

(cd $CONTRACT_DEPLOYMENT_DIR && truffle exec $DEPLOYER_SCRIPTS_DIR/load-build-artifacts.js --network production | pino-pretty)
(cd $CONTRACT_DEPLOYMENT_DIR && truffle deploy --network production)
(cd $CONTRACT_DEPLOYMENT_DIR && truffle exec $DEPLOYER_SCRIPTS_DIR/save-build-artifacts.js --network production | pino-pretty)
(cd $CONTRACT_DEPLOYMENT_DIR && truffle exec $DEPLOYER_SCRIPTS_DIR/self-test.js --network production | pino-pretty)
