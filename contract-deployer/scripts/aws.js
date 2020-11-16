const AWS = require('aws-sdk');

AWS.config.apiVersions = {
  s3: '2006-03-01'
};
AWS.config.endpoint = process.env.AWS_ENDPOINT_URL;
AWS.config.s3ForcePathStyle = process.env.AWS_ENDPOINT_URL!==undefined;

module.exports = AWS;
