// tslint:disable:no-consecutive-blank-lines ordered-imports align trailing-comma enum-naming
// tslint:disable:whitespace no-unbound-method no-trailing-whitespace
// tslint:disable:no-unused-variable
import {
  AwaitTransactionSuccessOpts,
  ContractFunctionObj,
  ContractTxFunctionObj,
  SendTransactionOpts,
  BaseContract,
  SubscriptionManager,
  PromiseWithTransactionHash,
  methodAbiToFunctionSignature,
  linkLibrariesInBytecode,
} from '@0x/base-contract';
import { schemas } from '@0x/json-schemas';
import {
  BlockParam,
  BlockParamLiteral,
  BlockRange,
  CallData,
  ContractAbi,
  ContractArtifact,
  DecodedLogArgs,
  LogWithDecodedArgs,
  MethodAbi,
  TransactionReceiptWithDecodedLogs,
  TxData,
  TxDataPayable,
  SupportedProvider,
} from 'ethereum-types';
import { BigNumber, classUtils, hexUtils, logUtils, providerUtils } from '@0x/utils';
import { EventCallback, IndexedFilterValues, SimpleContractArtifact } from '@0x/types';
import { Web3Wrapper } from '@0x/web3-wrapper';
import { assert } from '@0x/assert';
import * as ethers from 'ethers';
// tslint:enable:no-unused-variable

export type MerkleTreeMiMC_BLS12EventArgs =
  | MerkleTreeMiMC_BLS12NewLeafEventArgs
  | MerkleTreeMiMC_BLS12NewLeavesEventArgs;

export enum MerkleTreeMiMC_BLS12Events {
  NewLeaf = 'NewLeaf',
  NewLeaves = 'NewLeaves',
}

export interface MerkleTreeMiMC_BLS12NewLeafEventArgs extends DecodedLogArgs {
  leafIndex: BigNumber;
  leafValue: string;
  root: string;
}

export interface MerkleTreeMiMC_BLS12NewLeavesEventArgs extends DecodedLogArgs {
  minLeafIndex: BigNumber;
  leafValues: string[];
  root: string;
}

/* istanbul ignore next */
// tslint:disable:array-type
// tslint:disable:no-parameter-reassignment
// tslint:disable-next-line:class-name
export class MerkleTreeMiMC_BLS12Contract extends BaseContract {
  /**
   * @ignore
   */
  public static deployedBytecode: string | undefined;
  public static contractName = 'MerkleTreeMiMC_BLS12';
  private readonly _methodABIIndex: { [name: string]: number } = {};
  private readonly _subscriptionManager: SubscriptionManager<
    MerkleTreeMiMC_BLS12EventArgs,
    MerkleTreeMiMC_BLS12Events
  >;
  public static async deployFrom0xArtifactAsync(
    artifact: ContractArtifact | SimpleContractArtifact,
    supportedProvider: SupportedProvider,
    txDefaults: Partial<TxData>,
    logDecodeDependencies: {
      [contractName: string]: ContractArtifact | SimpleContractArtifact;
    },
  ): Promise<MerkleTreeMiMC_BLS12Contract> {
    assert.doesConformToSchema('txDefaults', txDefaults, schemas.txDataSchema, [
      schemas.addressSchema,
      schemas.numberSchema,
      schemas.jsNumber,
    ]);
    if (artifact.compilerOutput === undefined) {
      throw new Error('Compiler output not found in the artifact file');
    }
    const provider = providerUtils.standardizeOrThrow(supportedProvider);
    const bytecode = artifact.compilerOutput.evm.bytecode.object;
    const abi = artifact.compilerOutput.abi;
    const logDecodeDependenciesAbiOnly: {
      [contractName: string]: ContractAbi;
    } = {};
    if (Object.keys(logDecodeDependencies) !== undefined) {
      for (const key of Object.keys(logDecodeDependencies)) {
        logDecodeDependenciesAbiOnly[key] = logDecodeDependencies[key].compilerOutput.abi;
      }
    }
    return MerkleTreeMiMC_BLS12Contract.deployAsync(
      bytecode,
      abi,
      provider,
      txDefaults,
      logDecodeDependenciesAbiOnly,
    );
  }

  public static async deployWithLibrariesFrom0xArtifactAsync(
    artifact: ContractArtifact,
    libraryArtifacts: { [libraryName: string]: ContractArtifact },
    supportedProvider: SupportedProvider,
    txDefaults: Partial<TxData>,
    logDecodeDependencies: {
      [contractName: string]: ContractArtifact | SimpleContractArtifact;
    },
  ): Promise<MerkleTreeMiMC_BLS12Contract> {
    assert.doesConformToSchema('txDefaults', txDefaults, schemas.txDataSchema, [
      schemas.addressSchema,
      schemas.numberSchema,
      schemas.jsNumber,
    ]);
    if (artifact.compilerOutput === undefined) {
      throw new Error('Compiler output not found in the artifact file');
    }
    const provider = providerUtils.standardizeOrThrow(supportedProvider);
    const abi = artifact.compilerOutput.abi;
    const logDecodeDependenciesAbiOnly: {
      [contractName: string]: ContractAbi;
    } = {};
    if (Object.keys(logDecodeDependencies) !== undefined) {
      for (const key of Object.keys(logDecodeDependencies)) {
        logDecodeDependenciesAbiOnly[key] = logDecodeDependencies[key].compilerOutput.abi;
      }
    }
    const libraryAddresses = await MerkleTreeMiMC_BLS12Contract._deployLibrariesAsync(
      artifact,
      libraryArtifacts,
      new Web3Wrapper(provider),
      txDefaults,
    );
    const bytecode = linkLibrariesInBytecode(artifact, libraryAddresses);
    return MerkleTreeMiMC_BLS12Contract.deployAsync(
      bytecode,
      abi,
      provider,
      txDefaults,
      logDecodeDependenciesAbiOnly,
    );
  }

  public static async deployAsync(
    bytecode: string,
    abi: ContractAbi,
    supportedProvider: SupportedProvider,
    txDefaults: Partial<TxData>,
    logDecodeDependencies: { [contractName: string]: ContractAbi },
  ): Promise<MerkleTreeMiMC_BLS12Contract> {
    assert.isHexString('bytecode', bytecode);
    assert.doesConformToSchema('txDefaults', txDefaults, schemas.txDataSchema, [
      schemas.addressSchema,
      schemas.numberSchema,
      schemas.jsNumber,
    ]);
    const provider = providerUtils.standardizeOrThrow(supportedProvider);
    const constructorAbi = BaseContract._lookupConstructorAbi(abi);
    [] = BaseContract._formatABIDataItemList(
      constructorAbi.inputs,
      [],
      BaseContract._bigNumberToString,
    );
    const iface = new ethers.utils.Interface(abi);
    const deployInfo = iface.deployFunction;
    const txData = deployInfo.encode(bytecode, []);
    const web3Wrapper = new Web3Wrapper(provider);
    const txDataWithDefaults = await BaseContract._applyDefaultsToContractTxDataAsync(
      {
        data: txData,
        ...txDefaults,
      },
      web3Wrapper.estimateGasAsync.bind(web3Wrapper),
    );
    const txHash = await web3Wrapper.sendTransactionAsync(txDataWithDefaults);
    logUtils.log(`transactionHash: ${txHash}`);
    const txReceipt = await web3Wrapper.awaitTransactionSuccessAsync(txHash);
    logUtils.log(`MerkleTreeMiMC_BLS12 successfully deployed at ${txReceipt.contractAddress}`);
    const contractInstance = new MerkleTreeMiMC_BLS12Contract(
      txReceipt.contractAddress as string,
      provider,
      txDefaults,
      logDecodeDependencies,
    );
    contractInstance.constructorArgs = [];
    return contractInstance;
  }

  /**
   * @returns      The contract ABI
   */
  public static ABI(): ContractAbi {
    const abi = [
      {
        constant: true,
        inputs: [],
        name: 'treeHeight',
        outputs: [
          {
            name: '',
            type: 'uint256',
          },
        ],
        payable: false,
        stateMutability: 'view',
        type: 'function',
      },
      {
        constant: true,
        inputs: [],
        name: 'leafCount',
        outputs: [
          {
            name: '',
            type: 'uint256',
          },
        ],
        payable: false,
        stateMutability: 'view',
        type: 'function',
      },
      {
        constant: true,
        inputs: [
          {
            name: 'in_msgs',
            type: 'uint256[]',
          },
        ],
        name: 'mimc_bls12_377',
        outputs: [
          {
            name: '',
            type: 'uint256',
          },
        ],
        payable: false,
        stateMutability: 'pure',
        type: 'function',
      },
      {
        constant: true,
        inputs: [],
        name: 'treeWidth',
        outputs: [
          {
            name: '',
            type: 'uint256',
          },
        ],
        payable: false,
        stateMutability: 'view',
        type: 'function',
      },
      {
        constant: true,
        inputs: [],
        name: 'zero',
        outputs: [
          {
            name: '',
            type: 'uint256',
          },
        ],
        payable: false,
        stateMutability: 'view',
        type: 'function',
      },
      {
        constant: true,
        inputs: [
          {
            name: 'in_msgs',
            type: 'uint256[]',
          },
        ],
        name: 'mimcHash',
        outputs: [
          {
            name: '',
            type: 'uint256',
          },
        ],
        payable: false,
        stateMutability: 'pure',
        type: 'function',
      },
      {
        anonymous: false,
        inputs: [
          {
            name: 'leafIndex',
            type: 'uint256',
            indexed: false,
          },
          {
            name: 'leafValue',
            type: 'bytes32',
            indexed: false,
          },
          {
            name: 'root',
            type: 'bytes32',
            indexed: false,
          },
        ],
        name: 'NewLeaf',
        outputs: [],
        type: 'event',
      },
      {
        anonymous: false,
        inputs: [
          {
            name: 'minLeafIndex',
            type: 'uint256',
            indexed: false,
          },
          {
            name: 'leafValues',
            type: 'bytes32[]',
            indexed: false,
          },
          {
            name: 'root',
            type: 'bytes32',
            indexed: false,
          },
        ],
        name: 'NewLeaves',
        outputs: [],
        type: 'event',
      },
      {
        constant: true,
        inputs: [
          {
            name: 'leafIndex',
            type: 'uint256',
          },
        ],
        name: 'getFrontierSlot',
        outputs: [
          {
            name: 'slot',
            type: 'uint256',
          },
        ],
        payable: false,
        stateMutability: 'pure',
        type: 'function',
      },
      {
        constant: false,
        inputs: [
          {
            name: 'leafValue',
            type: 'bytes32',
          },
        ],
        name: 'insertLeaf',
        outputs: [
          {
            name: 'root',
            type: 'bytes32',
          },
        ],
        payable: false,
        stateMutability: 'nonpayable',
        type: 'function',
      },
      {
        constant: false,
        inputs: [
          {
            name: 'leafValues',
            type: 'bytes32[]',
          },
        ],
        name: 'insertLeaves',
        outputs: [
          {
            name: 'root',
            type: 'bytes32',
          },
        ],
        payable: false,
        stateMutability: 'nonpayable',
        type: 'function',
      },
    ] as ContractAbi;
    return abi;
  }

  protected static async _deployLibrariesAsync(
    artifact: ContractArtifact,
    libraryArtifacts: { [libraryName: string]: ContractArtifact },
    web3Wrapper: Web3Wrapper,
    txDefaults: Partial<TxData>,
    libraryAddresses: { [libraryName: string]: string } = {},
  ): Promise<{ [libraryName: string]: string }> {
    const links = artifact.compilerOutput.evm.bytecode.linkReferences;
    // Go through all linked libraries, recursively deploying them if necessary.
    for (const link of Object.values(links)) {
      for (const libraryName of Object.keys(link)) {
        if (!libraryAddresses[libraryName]) {
          // Library not yet deployed.
          const libraryArtifact = libraryArtifacts[libraryName];
          if (!libraryArtifact) {
            throw new Error(`Missing artifact for linked library "${libraryName}"`);
          }
          // Deploy any dependent libraries used by this library.
          await MerkleTreeMiMC_BLS12Contract._deployLibrariesAsync(
            libraryArtifact,
            libraryArtifacts,
            web3Wrapper,
            txDefaults,
            libraryAddresses,
          );
          // Deploy this library.
          const linkedLibraryBytecode = linkLibrariesInBytecode(libraryArtifact, libraryAddresses);
          const txDataWithDefaults = await BaseContract._applyDefaultsToContractTxDataAsync(
            {
              data: linkedLibraryBytecode,
              ...txDefaults,
            },
            web3Wrapper.estimateGasAsync.bind(web3Wrapper),
          );
          const txHash = await web3Wrapper.sendTransactionAsync(txDataWithDefaults);
          logUtils.log(`transactionHash: ${txHash}`);
          const { contractAddress } = await web3Wrapper.awaitTransactionSuccessAsync(txHash);
          logUtils.log(
            `${libraryArtifact.contractName} successfully deployed at ${contractAddress}`,
          );
          libraryAddresses[libraryArtifact.contractName] = contractAddress as string;
        }
      }
    }
    return libraryAddresses;
  }

  public getFunctionSignature(methodName: string): string {
    const index = this._methodABIIndex[methodName];
    const methodAbi = MerkleTreeMiMC_BLS12Contract.ABI()[index] as MethodAbi; // tslint:disable-line:no-unnecessary-type-assertion
    const functionSignature = methodAbiToFunctionSignature(methodAbi);
    return functionSignature;
  }

  public getABIDecodedTransactionData<T>(methodName: string, callData: string): T {
    const functionSignature = this.getFunctionSignature(methodName);
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    const abiEncoder = self._lookupAbiEncoder(functionSignature);
    const abiDecodedCallData = abiEncoder.strictDecode<T>(callData);
    return abiDecodedCallData;
  }

  public getABIDecodedReturnData<T>(methodName: string, callData: string): T {
    const functionSignature = this.getFunctionSignature(methodName);
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    const abiEncoder = self._lookupAbiEncoder(functionSignature);
    const abiDecodedCallData = abiEncoder.strictDecodeReturnValue<T>(callData);
    return abiDecodedCallData;
  }

  public getSelector(methodName: string): string {
    const functionSignature = this.getFunctionSignature(methodName);
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    const abiEncoder = self._lookupAbiEncoder(functionSignature);
    return abiEncoder.getSelector();
  }

  public treeHeight(): ContractFunctionObj<BigNumber> {
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    const functionSignature = 'treeHeight()';

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam,
      ): Promise<BigNumber> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock,
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(rawCallResult, abiEncoder);
        return abiEncoder.strictDecodeReturnValue<BigNumber>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, []);
      },
    };
  }
  public leafCount(): ContractFunctionObj<BigNumber> {
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    const functionSignature = 'leafCount()';

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam,
      ): Promise<BigNumber> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock,
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(rawCallResult, abiEncoder);
        return abiEncoder.strictDecodeReturnValue<BigNumber>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, []);
      },
    };
  }
  public mimc_bls12_377(in_msgs: BigNumber[]): ContractFunctionObj<BigNumber> {
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    assert.isArray('in_msgs', in_msgs);
    const functionSignature = 'mimc_bls12_377(uint256[])';

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam,
      ): Promise<BigNumber> {
        BaseContract._assertCallParams(callData, defaultBlock);
        let rawCallResult;
        if (self._deployedBytecodeIfExists) {
          rawCallResult = await self._evmExecAsync(this.getABIEncodedTransactionData());
        } else {
          rawCallResult = await self._performCallAsync(
            { data: this.getABIEncodedTransactionData(), ...callData },
            defaultBlock,
          );
        }
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(rawCallResult, abiEncoder);
        return abiEncoder.strictDecodeReturnValue<BigNumber>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [in_msgs]);
      },
    };
  }
  public treeWidth(): ContractFunctionObj<BigNumber> {
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    const functionSignature = 'treeWidth()';

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam,
      ): Promise<BigNumber> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock,
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(rawCallResult, abiEncoder);
        return abiEncoder.strictDecodeReturnValue<BigNumber>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, []);
      },
    };
  }
  public zero(): ContractFunctionObj<BigNumber> {
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    const functionSignature = 'zero()';

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam,
      ): Promise<BigNumber> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock,
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(rawCallResult, abiEncoder);
        return abiEncoder.strictDecodeReturnValue<BigNumber>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, []);
      },
    };
  }
  public mimcHash(in_msgs: BigNumber[]): ContractFunctionObj<BigNumber> {
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    assert.isArray('in_msgs', in_msgs);
    const functionSignature = 'mimcHash(uint256[])';

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam,
      ): Promise<BigNumber> {
        BaseContract._assertCallParams(callData, defaultBlock);
        let rawCallResult;
        if (self._deployedBytecodeIfExists) {
          rawCallResult = await self._evmExecAsync(this.getABIEncodedTransactionData());
        } else {
          rawCallResult = await self._performCallAsync(
            { data: this.getABIEncodedTransactionData(), ...callData },
            defaultBlock,
          );
        }
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(rawCallResult, abiEncoder);
        return abiEncoder.strictDecodeReturnValue<BigNumber>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [in_msgs]);
      },
    };
  }
  public getFrontierSlot(leafIndex: BigNumber): ContractFunctionObj<BigNumber> {
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    assert.isBigNumber('leafIndex', leafIndex);
    const functionSignature = 'getFrontierSlot(uint256)';

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam,
      ): Promise<BigNumber> {
        BaseContract._assertCallParams(callData, defaultBlock);
        let rawCallResult;
        if (self._deployedBytecodeIfExists) {
          rawCallResult = await self._evmExecAsync(this.getABIEncodedTransactionData());
        } else {
          rawCallResult = await self._performCallAsync(
            { data: this.getABIEncodedTransactionData(), ...callData },
            defaultBlock,
          );
        }
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(rawCallResult, abiEncoder);
        return abiEncoder.strictDecodeReturnValue<BigNumber>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [leafIndex]);
      },
    };
  }
  public insertLeaf(leafValue: string): ContractTxFunctionObj<string> {
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    assert.isString('leafValue', leafValue);
    const functionSignature = 'insertLeaf(bytes32)';

    return {
      async sendTransactionAsync(
        txData?: Partial<TxData> | undefined,
        opts: SendTransactionOpts = { shouldValidate: true },
      ): Promise<string> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync(
          { data: this.getABIEncodedTransactionData(), ...txData },
          this.estimateGasAsync.bind(this),
        );
        if (opts.shouldValidate !== false) {
          await this.callAsync(txDataWithDefaults);
        }
        return self._web3Wrapper.sendTransactionAsync(txDataWithDefaults);
      },
      awaitTransactionSuccessAsync(
        txData?: Partial<TxData>,
        opts: AwaitTransactionSuccessOpts = { shouldValidate: true },
      ): PromiseWithTransactionHash<TransactionReceiptWithDecodedLogs> {
        return self._promiseWithTransactionHash(this.sendTransactionAsync(txData, opts), opts);
      },
      async estimateGasAsync(txData?: Partial<TxData> | undefined): Promise<number> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync({
          data: this.getABIEncodedTransactionData(),
          ...txData,
        });
        return self._web3Wrapper.estimateGasAsync(txDataWithDefaults);
      },
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam,
      ): Promise<string> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock,
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(rawCallResult, abiEncoder);
        return abiEncoder.strictDecodeReturnValue<string>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [leafValue]);
      },
    };
  }
  public insertLeaves(leafValues: string[]): ContractTxFunctionObj<string> {
    const self = (this as any) as MerkleTreeMiMC_BLS12Contract;
    assert.isArray('leafValues', leafValues);
    const functionSignature = 'insertLeaves(bytes32[])';

    return {
      async sendTransactionAsync(
        txData?: Partial<TxData> | undefined,
        opts: SendTransactionOpts = { shouldValidate: true },
      ): Promise<string> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync(
          { data: this.getABIEncodedTransactionData(), ...txData },
          this.estimateGasAsync.bind(this),
        );
        if (opts.shouldValidate !== false) {
          await this.callAsync(txDataWithDefaults);
        }
        return self._web3Wrapper.sendTransactionAsync(txDataWithDefaults);
      },
      awaitTransactionSuccessAsync(
        txData?: Partial<TxData>,
        opts: AwaitTransactionSuccessOpts = { shouldValidate: true },
      ): PromiseWithTransactionHash<TransactionReceiptWithDecodedLogs> {
        return self._promiseWithTransactionHash(this.sendTransactionAsync(txData, opts), opts);
      },
      async estimateGasAsync(txData?: Partial<TxData> | undefined): Promise<number> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync({
          data: this.getABIEncodedTransactionData(),
          ...txData,
        });
        return self._web3Wrapper.estimateGasAsync(txDataWithDefaults);
      },
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam,
      ): Promise<string> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock,
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(rawCallResult, abiEncoder);
        return abiEncoder.strictDecodeReturnValue<string>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [leafValues]);
      },
    };
  }

  /**
   * Subscribe to an event type emitted by the MerkleTreeMiMC_BLS12 contract.
   * @param eventName The MerkleTreeMiMC_BLS12 contract event you would like to subscribe to.
   * @param indexFilterValues An object where the keys are indexed args returned by the event and
   * the value is the value you are interested in. E.g `{maker: aUserAddressHex}`
   * @param callback Callback that gets called when a log is added/removed
   * @param isVerbose Enable verbose subscription warnings (e.g recoverable network issues encountered)
   * @return Subscription token used later to unsubscribe
   */
  public subscribe<ArgsType extends MerkleTreeMiMC_BLS12EventArgs>(
    eventName: MerkleTreeMiMC_BLS12Events,
    indexFilterValues: IndexedFilterValues,
    callback: EventCallback<ArgsType>,
    isVerbose: boolean = false,
    blockPollingIntervalMs?: number,
  ): string {
    assert.doesBelongToStringEnum('eventName', eventName, MerkleTreeMiMC_BLS12Events);
    assert.doesConformToSchema(
      'indexFilterValues',
      indexFilterValues,
      schemas.indexFilterValuesSchema,
    );
    assert.isFunction('callback', callback);
    const subscriptionToken = this._subscriptionManager.subscribe<ArgsType>(
      this.address,
      eventName,
      indexFilterValues,
      MerkleTreeMiMC_BLS12Contract.ABI(),
      callback,
      isVerbose,
      blockPollingIntervalMs,
    );
    return subscriptionToken;
  }

  /**
   * Cancel a subscription
   * @param subscriptionToken Subscription token returned by `subscribe()`
   */
  public unsubscribe(subscriptionToken: string): void {
    this._subscriptionManager.unsubscribe(subscriptionToken);
  }

  /**
   * Cancels all existing subscriptions
   */
  public unsubscribeAll(): void {
    this._subscriptionManager.unsubscribeAll();
  }

  /**
   * Gets historical logs without creating a subscription
   * @param eventName The MerkleTreeMiMC_BLS12 contract event you would like to subscribe to.
   * @param blockRange Block range to get logs from.
   * @param indexFilterValues An object where the keys are indexed args returned by the event and
   * the value is the value you are interested in. E.g `{_from: aUserAddressHex}`
   * @return Array of logs that match the parameters
   */
  public async getLogsAsync<ArgsType extends MerkleTreeMiMC_BLS12EventArgs>(
    eventName: MerkleTreeMiMC_BLS12Events,
    blockRange: BlockRange,
    indexFilterValues: IndexedFilterValues,
  ): Promise<Array<LogWithDecodedArgs<ArgsType>>> {
    assert.doesBelongToStringEnum('eventName', eventName, MerkleTreeMiMC_BLS12Events);
    assert.doesConformToSchema('blockRange', blockRange, schemas.blockRangeSchema);
    assert.doesConformToSchema(
      'indexFilterValues',
      indexFilterValues,
      schemas.indexFilterValuesSchema,
    );
    const logs = await this._subscriptionManager.getLogsAsync<ArgsType>(
      this.address,
      eventName,
      blockRange,
      indexFilterValues,
      MerkleTreeMiMC_BLS12Contract.ABI(),
    );
    return logs;
  }

  constructor(
    address: string,
    supportedProvider: SupportedProvider,
    txDefaults?: Partial<TxData>,
    logDecodeDependencies?: { [contractName: string]: ContractAbi },
    deployedBytecode: string | undefined = MerkleTreeMiMC_BLS12Contract.deployedBytecode,
  ) {
    super(
      'MerkleTreeMiMC_BLS12',
      MerkleTreeMiMC_BLS12Contract.ABI(),
      address,
      supportedProvider,
      txDefaults,
      logDecodeDependencies,
      deployedBytecode,
    );
    classUtils.bindAll(this, ['_abiEncoderByFunctionSignature', 'address', '_web3Wrapper']);
    this._subscriptionManager = new SubscriptionManager<
      MerkleTreeMiMC_BLS12EventArgs,
      MerkleTreeMiMC_BLS12Events
    >(MerkleTreeMiMC_BLS12Contract.ABI(), this._web3Wrapper);
    MerkleTreeMiMC_BLS12Contract.ABI().forEach((item, index) => {
      if (item.type === 'function') {
        const methodAbi = item as MethodAbi;
        this._methodABIIndex[methodAbi.name] = index;
      }
    });
  }
}

// tslint:disable:max-file-line-count
// tslint:enable:no-unbound-method no-parameter-reassignment no-consecutive-blank-lines ordered-imports align
// tslint:enable:trailing-comma whitespace no-trailing-whitespace
