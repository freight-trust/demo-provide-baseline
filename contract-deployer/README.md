# README

ECS Task designed to deploy a given truffle contract and save/update build artifacts in a given S3 bucket.

In order to deploy the contract it must have:
1. Standard truffle project directory structure
1. Migration scripts

#### Configuration(Environment):
1. ```CONTRACT_DIR``` - truffle project directory, **default=**```/tmp/contract```
1. ```CONTRACT_BUCKET_NAME``` - bucket containing build artifacts
1. ```CONTRACT_KEY_PREFIX```  - key prefix for the build artifacts
1. ```TRUFFLE_NETWORK_ID``` -  ethereum network id on which contract will be deployed
1. ```TRUFFLE_BLOCKCHAIN_ENDPOINT``` - endpoint of the blockchain node used for the deployment
1. ```TRUFFLE_WALLET_PK``` - private key of the wallet that will perform the deployment

**Additional environment variables can be provided if migration scripts require them.**

#### Entrypoint Options:
1. ```-d[flag]``` - start deployment procedure
1. ```-s[str]``` - sleep before starting the deployment, uses ``sleep`` command argument format
1. ```-e[str]``` - start a contract(external) script after the deployment, value is a path to the script inside the contract directory
1. ```-c[flag] ``` - prevent this script from exiting after completion, usefull for docker debugging

#### Task Workflow:
1. Copy the contract truffle project into ```/tmp/contract-deployment```
1. Replace ```truffle-config.js```
1. Try to load existing build artifacts.
1. Deploy/Update the contract
1. Upload resulting build artifacts into the bucket
1. Perform self test to verify uploaded data
1. Run external scripts if provided
