const pino = require('pino');

const logger = pino({level: process.env.LOG_LEVEL || 'info', name:'Deployer', timestamp:false});

module.exports = {logger};
