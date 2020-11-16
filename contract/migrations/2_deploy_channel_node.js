const ChannelNode = artifacts.require("ChannelNode");

module.exports = function(deployer) {
  // ["JB"], ["JA"]
  const CHANNEL_NODE_DEPLOY_ARGS = JSON.parse(process.env.CHANNEL_NODE_DEPLOY_ARGS || "[]");
  // {}, {}
  const CHANNEL_NODE_DEPLOY_OPTS = JSON.parse(process.env.CHANNEL_NODE_DEPLOY_OPTS || "{}");
  console.log({CHANNEL_NODE_DEPLOY_ARGS});
  console.log({CHANNEL_NODE_DEPLOY_OPTS});
  if(Object.keys(CHANNEL_NODE_DEPLOY_OPTS).length !== 0){
    deployer.deploy(ChannelNode, CHANNEL_NODE_DEPLOY_ARGS, CHANNEL_NODE_DEPLOY_OPTS);
  }else{
    deployer.deploy(ChannelNode, CHANNEL_NODE_DEPLOY_ARGS);
  }
};
