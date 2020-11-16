const HDWalletProvider = require("@truffle/hdwallet-provider");

function getEnv(name, defaultValue){
  const value = process.env[name] || defaultValue;
  if(value === undefined){
    throw Error(`Missing "${name}" environment variable`);
  }
  return value;
}


const NETWORK_ID = getEnv('TRUFFLE_NETWORK_ID');
const WALLET_PK = getEnv('TRUFFLE_WALLET_PK');
const BLOCKCHAIN_ENDPOINT = getEnv('TRUFFLE_BLOCKCHAIN_ENDPOINT', null);



module.exports = {
  networks: {
    develop: {
      port: 8545,
      network_id: 15,
      accounts: 1,
      defaultEtherBalance: 500
    },
    production:{
      network_id: NETWORK_ID,
      provider: ()=> new HDWalletProvider([WALLET_PK], BLOCKCHAIN_ENDPOINT, 0)
    }
  }
}
