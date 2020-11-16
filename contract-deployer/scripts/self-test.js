const os = require('os');
const fs = require('fs').promises;
const _ = require('lodash');
const path = require('path');
const AWS = require('./aws');
const utils = require('./utils');
const {logger} = require('./logging');
const constants = require('./constants');
const loadBuildArtifacts = require('./load-build-artifacts-function.js');

async function main(){
  logger.info('Started: self-test...');
  utils.requireEnv([
    'CONTRACT_BUCKET_NAME'
  ]);
  const S3 = new AWS.S3();
  const bucket = process.env.CONTRACT_BUCKET_NAME;
  const prefix = process.env.CONTRACT_KEY_PREFIX || '';
  const tmpDirectory = await fs.mkdtemp(path.join(os.tmpdir(),'deployer_self_test_'));
  logger.info('Created temp dir %s', tmpDirectory);
  try{
    await loadBuildArtifacts(S3, bucket, prefix, tmpDirectory);
    const s3ArtifactFiles = await fs.readdir(tmpDirectory);
    const localArtifactFiles = await fs.readdir(constants.CONTRACT_BUILD_DIR);
    s3ArtifactFiles.sort();
    localArtifactFiles.sort();
    logger.info('Comparing artifact lists, local and S3...');
    logger.info('Local artifact files %O', localArtifactFiles);
    logger.info('S3 artifact files %O', s3ArtifactFiles);
    if(_.isEqual(s3ArtifactFiles, localArtifactFiles)){
      logger.info('Artifact lists are equal');
    }else{
      throw new Error('Artifact lists are not equal!');
    }
    logger.info('Comparing files...');
    for(const artifact of localArtifactFiles){
      const localArtifactFilename = path.join(constants.CONTRACT_BUILD_DIR, artifact);
      const s3ArtifactFilename = path.join(tmpDirectory, artifact);
      const localArtifactFile = await fs.readFile(localArtifactFilename);
      const s3ArtifactFile = await fs.readFile(s3ArtifactFilename);
      if(!localArtifactFile.equals(s3ArtifactFile)){
        throw new Error(`S3 ${artifact} != local ${artifact}`);
      }else{
        logger.info(`S3 ${artifact} = local ${artifact}`);
      }
    }
  }catch(e){
    if(e.code == 'NoSuchKey'){
      throw Error(`bucket:${process.env.CONTRACT_BUCKET_NAME}//${key} not found`);
    }else{
      throw e;
    }
  }
  logger.info('Completed: self-test');
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
