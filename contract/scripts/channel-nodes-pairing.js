const fs = require('fs').promises;
const path = require('path');
const utils = require('/deployer/scripts/utils');
const AWS = require('/deployer/scripts/aws');
const {logger} = require('/deployer/scripts/logging');
const ChannelNode = artifacts.require("ChannelNode");

async function main(){
  logger.info('Start: channel nodes pairing');
  const config = JSON.parse(process.env.CHANNEL_NODES_PAIRING_CONFIG);
  const S3 = new AWS.S3();
  while(!await utils.S3.exists(S3, config.build.artifact.bucket, config.build.artifact.key)){
    await utils.sleep(3);
  }
  const artifact = await utils.S3.loadJSON(S3, config.build.artifact.bucket, config.build.artifact.key);
  const address = artifact.networks[config.network].address;
  const our = await ChannelNode.deployed();
  const ourOwner = await our.owner.call();
  const their = await ChannelNode.at(address);
  const theirOwner = await their.owner.call();
  logger.info('Our contract address:%s, owner:%s, participant: %s', our.address, ourOwner, config.participant.our);
  logger.info('Their contract address:%s, owner:%s, participant: %s', their.address, theirOwner, config.participant.their);
  logger.info('our.addParticipant(%s, %s)', config.participant.their, theirOwner);
  await our.addParticipant(config.participant.their, theirOwner);
  let participant = await their.getParticipant(config.participant.our);
  while(participant.participantAddress != ourOwner){
    logger.info('Our participant %s not yet added to their contract', config.participant.our);
    await utils.sleep(5);
    participant = await their.getParticipant(config.participant.our);
  }
  logger.info('their.updateParticipantContractAddress(%s,%s)', config.participant.our, our.address)
  await their.updateParticipantContractAddress(config.participant.our, our.address);
  logger.info('Done: channel nodes pairing');
}



module.exports = async function(done){
  try{
    await main();
    done()
  }catch(e){
    console.error(e);
    process.exit(1);
  }
}
