const fs = require('fs').promises;
const path = require('path');
const utils = require('./utils');
const AWS = require('./aws');
const {logger} = require('./logging');
const constants = require('./constants');
const loadBuildArtifacts = require('./load-build-artifacts-function.js');

async function main(){
  logger.info('Started: load-build-artifacts...');
  utils.requireEnv([
    'CONTRACT_BUCKET_NAME'
  ]);
  const S3 = new AWS.S3();
  const bucket = process.env.CONTRACT_BUCKET_NAME;
  const prefix = process.env.CONTRACT_KEY_PREFIX || '';
  await loadBuildArtifacts(S3, bucket, prefix, constants.CONTRACT_BUILD_DIR);
  logger.info('Completed: load-build-artifacts');
}

module.exports = async function(done){
  try{
    await main();
    done()
  }catch(e){
    logger.error('%s', e);
    process.exit(1);
  }
}
