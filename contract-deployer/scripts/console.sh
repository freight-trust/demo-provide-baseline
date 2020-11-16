#!/usr/bin/env bash

source /deployer/scripts/base.sh

(cd $CONTRACT_DEPLOYMENT_DIR && truffle console --network production)
