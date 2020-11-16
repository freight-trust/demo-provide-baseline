const fs = require('fs').promises;
const path = require('path');
const AWS = require('./aws');
const utils = require('./utils');
const {logger} = require('./logging');
const constants = require('./constants');


async function main(){
  logger.info('Started: save-build-artifacts...');
  utils.requireEnv([
    'CONTRACT_BUCKET_NAME'
  ]);
  const S3 = new AWS.S3();
  const prefix = process.env.CONTRACT_KEY_PREFIX || '';
  const bucketName = process.env.CONTRACT_BUCKET_NAME;
  const artifactNames = await fs.readdir(constants.CONTRACT_BUILD_DIR);
  for(const artifactName of artifactNames){
    const artifactFile = path.join(constants.CONTRACT_BUILD_DIR, artifactName);
    const artifactS3Key = path.join(prefix, artifactName);
    await utils.S3.saveFile(S3, artifactFile, bucketName, artifactS3Key);
  };
  logger.info('Completed: save-build-artifacts');
}

module.exports = async function(done){
  try{
    await main();
    done();
  }catch(e){
    logger.error(e);
    process.exit(1);
  }
}
