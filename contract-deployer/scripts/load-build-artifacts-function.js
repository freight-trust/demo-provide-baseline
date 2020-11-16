const path = require('path');
const utils = require('./utils');
const {logger} = require('./logging');


async function loadBuildArtifacts(S3, bucket, prefix, dirname){
  logger.info('Loading build artifacts bucket://%s/%s" -> "%s"...', bucket, prefix, dirname);
  const artifactObjects = await utils.S3.listObjects(S3, bucket, prefix);
  for(const artifactObject of artifactObjects){
    const artifactKey = artifactObject.Key;
    const artifactFilename = path.join(dirname, path.relative(prefix, artifactKey));
    await utils.S3.loadToFile(S3, bucket, artifactKey, artifactFilename);
  }
  logger.info('Build artifacts loading completed');
}

module.exports = loadBuildArtifacts;
