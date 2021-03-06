/**
@author iAmMichaelConnor
*/

// import assert from 'assert';
import config from 'config';
import Web3 from '../src/web3';
import deployer from './rest/deployer';

const web3 = Web3.connect();

const contractName = config.contractNames[0];
let contractInstance;
let coinbase;

const numberOfBatches = 1;
const batchSize = 128;

describe(`${contractName}`, async () => {
  before('get contractInstance', async () => {
    if (!(await Web3.isConnected())) await Web3.connection();

    coinbase = await web3.eth.getCoinbase();

    contractInstance = await deployer.getContractInstance(contractName);
  });

  // eslint-disable-next-line func-names
  describe(`mimc hashing via ${contractName}`, async function () {
    this.timeout(3660000); // surprisingly, this.timeout() doesn't work inside an arrow function!

    // console.log('in config', config.contractNames, config.HASH_TYPE);
    // console.log('in docker-compose', process.env.HASH_TYPE);
    const gasUsedArray = [];
    let totalGasUsed = 0;
    let averageGasUsed = 0;
    let averageGasUsedMinusTxCost = 0;
    let max = 0;
    let min = 100000000;
    let range;

    it(`hashes correctly`, async () => {
      if (process.env.HASH_TYPE === 'mimc') {
        let txReceipt;
        for (let i = 0; i < 32; i += 1) {
          if (process.env.CURVE === 'BLS12_377') {
            // eslint-disable-next-line no-await-in-loop
            txReceipt = await contractInstance.methods.mimcHash([i, i + 1]).send({
              from: coinbase,
              gas: config.web3.options.defaultGas,
              gasPrice: config.web3.options.defaultGasPrice,
            });
          } else {
            // eslint-disable-next-line no-await-in-loop
            txReceipt = await contractInstance.methods.mimcHash2(i, i + 1).send({
              from: coinbase,
              gas: config.web3.options.defaultGas,
              gasPrice: config.web3.options.defaultGasPrice,
            });
          }
          const { gasUsed } = txReceipt;
          gasUsedArray.push(gasUsed);
        }
      } else {
        console.log('This test is disabled for SHA hashing.');
      }
    });

    if (process.env.HASH_TYPE === 'mimc') {
      after('provide summary stats', async () => {
        totalGasUsed = gasUsedArray.reduce((acc, cur) => acc + cur);
        max = Math.max(...gasUsedArray);
        min = Math.min(...gasUsedArray);
        averageGasUsed = totalGasUsed / batchSize;
        averageGasUsedMinusTxCost = averageGasUsed - 21000;
        range = max - min;
        // console.log('gasUsedArray:');
        // console.dir(gasUsedArray, { maxArrayLength: null });
        console.log('totalGasUsed:', totalGasUsed);
        console.log('averageGasUsed:', averageGasUsed);
        console.log('averageGasUsedMinusTxCost:', averageGasUsedMinusTxCost);
        console.log('min:', min);
        console.log('max:', max);
        console.log('range:', range);
      });
    }
  });

  // eslint-disable-next-line func-names
  describe(`adding leaves (one-at-a-time) via ${contractName}`, async function () {
    this.timeout(3660000); // surprisingly, this.timeout() doesn't work inside an arrow function!

    // console.log('in config', config.contractNames, config.HASH_TYPE);
    // console.log('in docker-compose', process.env.HASH_TYPE);
    const gasUsedArray = [];
    let totalGasUsed = 0;
    let averageGasUsed = 0;
    let averageGasUsedMinusTxCost = 0;
    let max = 0;
    let min = 100000000;
    let range;

    it(`adds one leaf at a time correctly`, async () => {
      for (let i = 0; i < batchSize; i += 1) {
        const leaf = i.toString().padStart(64, '0'); // pad to 32 bytes

        // eslint-disable-next-line no-await-in-loop
        const txReceipt = await contractInstance.methods
          ._insertLeaf(`0x${leaf}`)
          .send({
            from: coinbase,
            gas: config.web3.options.defaultGas,
            gasPrice: config.web3.options.defaultGasPrice,
          })
          // eslint-disable-next-line no-loop-func
          .on('receipt', (receipt) => {
            const { leafIndex, leafValue, root } = receipt.events.NewLeaf.returnValues;
            console.log('NewLeaf event returnValues:', leafIndex, leafValue, root);

            // // For debugging the hash function:
            // const outputs = receipt.events.Output.map(event => {
            //   const { leftInput, rightInput, output, nodeIndex } = event.returnValues;
            //   return { leftInput, rightInput, output, nodeIndex };
            // });
            // console.log('outputs:', outputs);
          });
        const { gasUsed } = txReceipt;
        gasUsedArray.push(gasUsed);
      }
    });

    after('provide summary stats', async () => {
      totalGasUsed = gasUsedArray.reduce((acc, cur) => acc + cur);
      max = Math.max(...gasUsedArray);
      min = Math.min(...gasUsedArray);
      averageGasUsed = totalGasUsed / batchSize;
      averageGasUsedMinusTxCost = averageGasUsed - 21000;
      range = max - min;
      console.log('gasUsedArray:');
      console.dir(gasUsedArray, { maxArrayLength: null });
      console.log('totalGasUsed:', totalGasUsed);
      console.log('averageGasUsed:', averageGasUsed);
      console.log('averageGasUsedMinusTxCost:', averageGasUsedMinusTxCost);
      console.log('min:', min);
      console.log('max:', max);
      console.log('range:', range);
    });
  });

  // eslint-disable-next-line func-names
  describe(`Adding ${batchSize} leaves at once`, async function () {
    this.timeout(3660000); // surprisingly, this.timeout() doesn't work inside an arrow function!

    const gasUsedArray = [];
    let totalGasUsed = 0;
    let averageGasUsed = 0;
    let averageGasUsedMinusTxCost = 0;

    it(`Adds the leaves`, async () => {
      // create the leafValues to add:
      const leaves = [];
      for (let i = 0; i < batchSize; i += 1) {
        const leaf = i.toString().padStart(64, '0'); // pad to 32 bytes
        leaves.push(`0x${leaf}`);
      }
      // eslint-disable-next-line no-await-in-loop
      const txReceipt = await contractInstance.methods
        ._insertLeaves(leaves)
        .send({
          from: coinbase,
          gas: 10000000, // explore a full block of gas being used
          gasPrice: config.web3.options.defaultGasPrice,
        })
        // eslint-disable-next-line no-loop-func
        .on('receipt', (receipt) => {
          const { minLeafIndex, leafValues, root } = receipt.events.NewLeaves.returnValues;

          console.log('NewLeaves event returnValues:', minLeafIndex, leafValues, root);

          // console.dir(receipt.events, { depth: null });
        });

      const { gasUsed } = txReceipt;
      gasUsedArray.push(gasUsed);
    });

    after('provide summary stats', async () => {
      totalGasUsed = gasUsedArray.reduce((acc, cur) => acc + cur);
      averageGasUsed = totalGasUsed / batchSize;
      averageGasUsedMinusTxCost = (totalGasUsed - 21000) / batchSize;
      console.log('\ngasUsedArray:');
      console.dir(gasUsedArray, { maxArrayLength: null });
      console.log('totalGasUsed:', totalGasUsed);
      console.log('averageGasUsed:', averageGasUsed);
      console.log('averageGasUsedMinusTxCost:', averageGasUsedMinusTxCost);
    });
  });
  //
  // // eslint-disable-next-line func-names, prettier/prettier
  // describe(`Adding ${numberOfBatches * batchSize} leaves in batches of ${batchSize}`, async function() {
  //   this.timeout(3660000); // surprisingly, this.timeout() doesn't work inside an arrow function!
  //
  //   const numberOfLeaves = numberOfBatches * batchSize;
  //   const gasUsedArray = [];
  //   let totalGasUsed = 0;
  //   let averageGasUsed = 0;
  //   let averageGasUsedMinusTxCost = 0;
  //
  //   it(`Adds the leaves`, async () => {
  //     // create the leafValues to add:
  //     const leaves = [];
  //     for (let i = 0; i < numberOfLeaves; i += 1) {
  //       const leaf = i.toString().padStart(64, '0'); // pad to 32 bytes
  //       leaves.push(`0x${leaf}`);
  //     }
  //
  //     for (let i = 0; i < numberOfBatches; i++) {
  //       const leavesToInsert = leaves.slice(i * batchSize, (i + 1) * batchSize);
  //       // eslint-disable-next-line no-await-in-loop
  //       const txReceipt = await contractInstance.methods
  //         ._insertLeaves(leavesToInsert)
  //         .send({
  //           from: coinbase,
  //           gas: 8000000, // explore a full block of gas being used
  //           gasPrice: config.web3.options.defaultGasPrice,
  //         })
  //         // eslint-disable-next-line no-loop-func
  //         .on('receipt', receipt => {
  //           const { minLeafIndex, leafValues, root } = receipt.events.NewLeaves.returnValues;
  //
  //           console.log('NewLeaves event returnValues:', minLeafIndex, leafValues, root);
  //
  //           // console.dir(receipt.events, { depth: null });
  //         });
  //
  //       const { gasUsed } = txReceipt;
  //       gasUsedArray.push(gasUsed);
  //     }
  //   });
  //
  //   after('provide summary stats', async () => {
  //     totalGasUsed = gasUsedArray.reduce((acc, cur) => acc + cur);
  //     averageGasUsed = totalGasUsed / batchSize;
  //     averageGasUsedMinusTxCost = (totalGasUsed - 21000) / batchSize;
  //     console.log('\ngasUsedArray:');
  //     console.dir(gasUsedArray, { maxArrayLength: null });
  //     console.log('totalGasUsed:', totalGasUsed);
  //     console.log('averageGasUsed:', averageGasUsed);
  //     console.log('averageGasUsedMinusTxCost:', averageGasUsedMinusTxCost);
  //   });
  // });
});
