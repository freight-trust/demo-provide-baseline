const path = require('path');

const CONTRACT_DEPLOYMENT_DIR = '/tmp/contract-deployment';
const CONTRACT_BUILD_DIR = path.join(CONTRACT_DEPLOYMENT_DIR, 'build/contracts');

module.exports = {
  CONTRACT_DEPLOYMENT_DIR,
  CONTRACT_BUILD_DIR
}
