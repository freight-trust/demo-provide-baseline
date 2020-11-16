const fs = require('fs').promises;
const {exec} = require('child_process');
const path = require('path');
const md5 = require('md5');
const {logger} = require('./logging');

module.exports = {
  sleep: async function(seconds) {
    logger.info('Sleep for %s second(s)', seconds);
    return new Promise(resolve => setTimeout(resolve, seconds*1000));
  },
  requireEnv: function(requiredEnvVarsNames){
    logger.info('Checking required environment variables...');
    for(const name of requiredEnvVarsNames){
      if(process.env[name] === undefined){
        throw Error(`Missing required env variable "${name}"`)
      }else{
        logger.info('%s="%s"', name, process.env[name]);
      }
    }
    logger.info('Required environment variables are in place.')
  },
  fs:{
    listdirfiles: async function(dirname){
      return (await fs.readdir(dirname)).map(p=>path.join(dirname, p));
    }
  },
  S3: {
    saveFile: async function(S3, filename, Bucket, Key){
      logger.info('Saving %s -> bucket://%s/%s...', filename, Bucket, Key);
      const filedata = await fs.readFile(filename);
      await S3.putObject({
        Body: filedata,
        ContentMD5: new Buffer(md5(filedata), 'hex').toString('base64'),
        Bucket,
        Key
      }).promise();
      logger.info('Saved');
    },
    exists: async function(S3, Bucket, Key){
      logger.info('Checking existence of S3 object bucket://%s/%s ...', Bucket, Key);
      try{
        const response = await S3.headObject({
          Bucket,
          Key
        }).promise();
        logger.info('Object found');
        return true;
      }catch(e){
        if(e.code === 'NotFound'){
          logger.info('Object not found');
          return false;
        }
        throw e;
      }
    },
    loadJSON: async function(S3, Bucket, Key){
      logger.info('Loading S3 object bucket://%s/%s as JSON...', Key, Bucket);
      const response = await S3.getObject({
        Bucket,
        Key
      }).promise();
      return JSON.parse(response.Body);
    },
    loadToFile: async function(S3, Bucket, Key, filename){
      logger.info('Saving S3 object bucket://%s/%s -> %s"...',Bucket, Key, filename);
      logger.info('Loading file from S3...');
      const response = await S3.getObject({
        Bucket,
        Key
      }).promise();
      logger.info('Loaded. Saving file to FS...');
      const dirname = path.dirname(filename);
      await fs.mkdir(dirname, {recursive: true});
      await fs.writeFile(filename, response.Body);
      logger.info('Saved');
    },
    listObjects: async function(S3, Bucket, Prefix, MaxKeys){
      logger.info('Listing objects bucket://%s/%s...', Bucket, Prefix);
      if (MaxKeys !== undefined){
        logger.info('Max keys per page %s', MaxKeys);
      }
      const objects = [];
      let ContinuationToken = undefined;
      let page = 1;
      while(true){
        logger.info('Loading objects, page %s', page);
        const data = await S3.listObjectsV2({
          Bucket,
          Prefix,
          MaxKeys,
          ContinuationToken
        }).promise();
        logger.info('Page loaded. Found %s object(s)', data.Contents.length);
        for(const object of data.Contents){
          objects.push(object);
        }
        if(!data.IsTruncated){
          logger.info('Last page');
          break;
        }else{
          ContinuationToken = data.NextContinuationToken;
        }
      }
      logger.info('Found %s object(s)', objects.length);
      return objects;
    }
  }
}
