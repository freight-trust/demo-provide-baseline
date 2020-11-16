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
} from "@0x/base-contract";
import { schemas } from "@0x/json-schemas";
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
} from "ethereum-types";
import {
  BigNumber,
  classUtils,
  hexUtils,
  logUtils,
  providerUtils,
} from "@0x/utils";
import {
  EventCallback,
  IndexedFilterValues,
  SimpleContractArtifact,
} from "@0x/types";
import { Web3Wrapper } from "@0x/web3-wrapper";
import { assert } from "@0x/assert";
import * as ethers from "ethers";
// tslint:enable:no-unused-variable

export type MultipleMerkleTreesControllerSHAEventArgs =
  | MultipleMerkleTreesControllerSHANewLeafAEventArgs
  | MultipleMerkleTreesControllerSHANewLeavesAEventArgs
  | MultipleMerkleTreesControllerSHANewLeafBEventArgs
  | MultipleMerkleTreesControllerSHANewLeavesBEventArgs;

export enum MultipleMerkleTreesControllerSHAEvents {
  NewLeafA = "NewLeafA",
  NewLeavesA = "NewLeavesA",
  NewLeafB = "NewLeafB",
  NewLeavesB = "NewLeavesB",
}

export interface MultipleMerkleTreesControllerSHANewLeafAEventArgs
  extends DecodedLogArgs {
  leafIndex: BigNumber;
  leafValue: string;
  root: string;
}

export interface MultipleMerkleTreesControllerSHANewLeavesAEventArgs
  extends DecodedLogArgs {
  minLeafIndex: BigNumber;
  leafValues: string[];
  root: string;
}

export interface MultipleMerkleTreesControllerSHANewLeafBEventArgs
  extends DecodedLogArgs {
  leafIndex: BigNumber;
  leafValue: string;
  root: string;
}

export interface MultipleMerkleTreesControllerSHANewLeavesBEventArgs
  extends DecodedLogArgs {
  minLeafIndex: BigNumber;
  leafValues: string[];
  root: string;
}

/* istanbul ignore next */
// tslint:disable:array-type
// tslint:disable:no-parameter-reassignment
// tslint:disable-next-line:class-name
export class MultipleMerkleTreesControllerSHAContract extends BaseContract {
  /**
   * @ignore
   */
  public static deployedBytecode: string | undefined;
  public static contractName = "MultipleMerkleTreesControllerSHA";
  private readonly _methodABIIndex: { [name: string]: number } = {};
  private readonly _subscriptionManager: SubscriptionManager<
    MultipleMerkleTreesControllerSHAEventArgs,
    MultipleMerkleTreesControllerSHAEvents
  >;
  public static async deployFrom0xArtifactAsync(
    artifact: ContractArtifact | SimpleContractArtifact,
    supportedProvider: SupportedProvider,
    txDefaults: Partial<TxData>,
    logDecodeDependencies: {
      [contractName: string]: ContractArtifact | SimpleContractArtifact;
    }
  ): Promise<MultipleMerkleTreesControllerSHAContract> {
    assert.doesConformToSchema("txDefaults", txDefaults, schemas.txDataSchema, [
      schemas.addressSchema,
      schemas.numberSchema,
      schemas.jsNumber,
    ]);
    if (artifact.compilerOutput === undefined) {
      throw new Error("Compiler output not found in the artifact file");
    }
    const provider = providerUtils.standardizeOrThrow(supportedProvider);
    const bytecode = artifact.compilerOutput.evm.bytecode.object;
    const abi = artifact.compilerOutput.abi;
    const logDecodeDependenciesAbiOnly: {
      [contractName: string]: ContractAbi;
    } = {};
    if (Object.keys(logDecodeDependencies) !== undefined) {
      for (const key of Object.keys(logDecodeDependencies)) {
        logDecodeDependenciesAbiOnly[key] =
          logDecodeDependencies[key].compilerOutput.abi;
      }
    }
    return MultipleMerkleTreesControllerSHAContract.deployAsync(
      bytecode,
      abi,
      provider,
      txDefaults,
      logDecodeDependenciesAbiOnly
    );
  }

  public static async deployWithLibrariesFrom0xArtifactAsync(
    artifact: ContractArtifact,
    libraryArtifacts: { [libraryName: string]: ContractArtifact },
    supportedProvider: SupportedProvider,
    txDefaults: Partial<TxData>,
    logDecodeDependencies: {
      [contractName: string]: ContractArtifact | SimpleContractArtifact;
    }
  ): Promise<MultipleMerkleTreesControllerSHAContract> {
    assert.doesConformToSchema("txDefaults", txDefaults, schemas.txDataSchema, [
      schemas.addressSchema,
      schemas.numberSchema,
      schemas.jsNumber,
    ]);
    if (artifact.compilerOutput === undefined) {
      throw new Error("Compiler output not found in the artifact file");
    }
    const provider = providerUtils.standardizeOrThrow(supportedProvider);
    const abi = artifact.compilerOutput.abi;
    const logDecodeDependenciesAbiOnly: {
      [contractName: string]: ContractAbi;
    } = {};
    if (Object.keys(logDecodeDependencies) !== undefined) {
      for (const key of Object.keys(logDecodeDependencies)) {
        logDecodeDependenciesAbiOnly[key] =
          logDecodeDependencies[key].compilerOutput.abi;
      }
    }
    const libraryAddresses = await MultipleMerkleTreesControllerSHAContract._deployLibrariesAsync(
      artifact,
      libraryArtifacts,
      new Web3Wrapper(provider),
      txDefaults
    );
    const bytecode = linkLibrariesInBytecode(artifact, libraryAddresses);
    return MultipleMerkleTreesControllerSHAContract.deployAsync(
      bytecode,
      abi,
      provider,
      txDefaults,
      logDecodeDependenciesAbiOnly
    );
  }

  public static async deployAsync(
    bytecode: string,
    abi: ContractAbi,
    supportedProvider: SupportedProvider,
    txDefaults: Partial<TxData>,
    logDecodeDependencies: { [contractName: string]: ContractAbi }
  ): Promise<MultipleMerkleTreesControllerSHAContract> {
    assert.isHexString("bytecode", bytecode);
    assert.doesConformToSchema("txDefaults", txDefaults, schemas.txDataSchema, [
      schemas.addressSchema,
      schemas.numberSchema,
      schemas.jsNumber,
    ]);
    const provider = providerUtils.standardizeOrThrow(supportedProvider);
    const constructorAbi = BaseContract._lookupConstructorAbi(abi);
    [] = BaseContract._formatABIDataItemList(
      constructorAbi.inputs,
      [],
      BaseContract._bigNumberToString
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
      web3Wrapper.estimateGasAsync.bind(web3Wrapper)
    );
    const txHash = await web3Wrapper.sendTransactionAsync(txDataWithDefaults);
    logUtils.log(`transactionHash: ${txHash}`);
    const txReceipt = await web3Wrapper.awaitTransactionSuccessAsync(txHash);
    logUtils.log(
      `MultipleMerkleTreesControllerSHA successfully deployed at ${txReceipt.contractAddress}`
    );
    const contractInstance = new MultipleMerkleTreesControllerSHAContract(
      txReceipt.contractAddress as string,
      provider,
      txDefaults,
      logDecodeDependencies
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
        inputs: [
          {
            name: "index_0",
            type: "uint256",
          },
        ],
        name: "latestRoot",
        outputs: [
          {
            name: "",
            type: "bytes32",
          },
        ],
        payable: false,
        stateMutability: "view",
        type: "function",
      },
      {
        constant: true,
        inputs: [],
        name: "treeHeight_a",
        outputs: [
          {
            name: "",
            type: "uint256",
          },
        ],
        payable: false,
        stateMutability: "view",
        type: "function",
      },
      {
        constant: true,
        inputs: [],
        name: "treeHeight_b",
        outputs: [
          {
            name: "",
            type: "uint256",
          },
        ],
        payable: false,
        stateMutability: "view",
        type: "function",
      },
      {
        constant: false,
        inputs: [
          {
            name: "leafValue",
            type: "bytes32",
          },
          {
            name: "tree",
            type: "uint256",
          },
        ],
        name: "insertLeaf",
        outputs: [
          {
            name: "root",
            type: "bytes32",
          },
        ],
        payable: false,
        stateMutability: "nonpayable",
        type: "function",
      },
      {
        constant: true,
        inputs: [],
        name: "owner",
        outputs: [
          {
            name: "",
            type: "address",
          },
        ],
        payable: false,
        stateMutability: "view",
        type: "function",
      },
      {
        constant: true,
        inputs: [
          {
            name: "index_0",
            type: "bytes32",
          },
        ],
        name: "roots",
        outputs: [
          {
            name: "",
            type: "bytes32",
          },
        ],
        payable: false,
        stateMutability: "view",
        type: "function",
      },
      {
        constant: false,
        inputs: [
          {
            name: "leafValues",
            type: "bytes32[]",
          },
          {
            name: "tree",
            type: "uint256",
          },
        ],
        name: "insertLeaves",
        outputs: [
          {
            name: "root",
            type: "bytes32",
          },
        ],
        payable: false,
        stateMutability: "nonpayable",
        type: "function",
      },
      {
        constant: true,
        inputs: [
          {
            name: "index_0",
            type: "uint256",
          },
        ],
        name: "leafCount",
        outputs: [
          {
            name: "",
            type: "uint256",
          },
        ],
        payable: false,
        stateMutability: "view",
        type: "function",
      },
      {
        inputs: [],
        outputs: [],
        payable: false,
        stateMutability: "nonpayable",
        type: "constructor",
      },
      {
        anonymous: false,
        inputs: [
          {
            name: "leafIndex",
            type: "uint256",
            indexed: false,
          },
          {
            name: "leafValue",
            type: "bytes32",
            indexed: false,
          },
          {
            name: "root",
            type: "bytes32",
            indexed: false,
          },
        ],
        name: "NewLeafA",
        outputs: [],
        type: "event",
      },
      {
        anonymous: false,
        inputs: [
          {
            name: "minLeafIndex",
            type: "uint256",
            indexed: false,
          },
          {
            name: "leafValues",
            type: "bytes32[]",
            indexed: false,
          },
          {
            name: "root",
            type: "bytes32",
            indexed: false,
          },
        ],
        name: "NewLeavesA",
        outputs: [],
        type: "event",
      },
      {
        anonymous: false,
        inputs: [
          {
            name: "leafIndex",
            type: "uint256",
            indexed: false,
          },
          {
            name: "leafValue",
            type: "bytes32",
            indexed: false,
          },
          {
            name: "root",
            type: "bytes32",
            indexed: false,
          },
        ],
        name: "NewLeafB",
        outputs: [],
        type: "event",
      },
      {
        anonymous: false,
        inputs: [
          {
            name: "minLeafIndex",
            type: "uint256",
            indexed: false,
          },
          {
            name: "leafValues",
            type: "bytes32[]",
            indexed: false,
          },
          {
            name: "root",
            type: "bytes32",
            indexed: false,
          },
        ],
        name: "NewLeavesB",
        outputs: [],
        type: "event",
      },
      {
        constant: false,
        inputs: [
          {
            name: "leafValue",
            type: "bytes32",
          },
          {
            name: "tree",
            type: "uint256",
          },
        ],
        name: "_insertLeaf",
        outputs: [],
        payable: false,
        stateMutability: "nonpayable",
        type: "function",
      },
      {
        constant: false,
        inputs: [
          {
            name: "leafValues",
            type: "bytes32[]",
          },
          {
            name: "tree",
            type: "uint256",
          },
        ],
        name: "_insertLeaves",
        outputs: [],
        payable: false,
        stateMutability: "nonpayable",
        type: "function",
      },
    ] as ContractAbi;
    return abi;
  }

  protected static async _deployLibrariesAsync(
    artifact: ContractArtifact,
    libraryArtifacts: { [libraryName: string]: ContractArtifact },
    web3Wrapper: Web3Wrapper,
    txDefaults: Partial<TxData>,
    libraryAddresses: { [libraryName: string]: string } = {}
  ): Promise<{ [libraryName: string]: string }> {
    const links = artifact.compilerOutput.evm.bytecode.linkReferences;
    // Go through all linked libraries, recursively deploying them if necessary.
    for (const link of Object.values(links)) {
      for (const libraryName of Object.keys(link)) {
        if (!libraryAddresses[libraryName]) {
          // Library not yet deployed.
          const libraryArtifact = libraryArtifacts[libraryName];
          if (!libraryArtifact) {
            throw new Error(
              `Missing artifact for linked library "${libraryName}"`
            );
          }
          // Deploy any dependent libraries used by this library.
          await MultipleMerkleTreesControllerSHAContract._deployLibrariesAsync(
            libraryArtifact,
            libraryArtifacts,
            web3Wrapper,
            txDefaults,
            libraryAddresses
          );
          // Deploy this library.
          const linkedLibraryBytecode = linkLibrariesInBytecode(
            libraryArtifact,
            libraryAddresses
          );
          const txDataWithDefaults = await BaseContract._applyDefaultsToContractTxDataAsync(
            {
              data: linkedLibraryBytecode,
              ...txDefaults,
            },
            web3Wrapper.estimateGasAsync.bind(web3Wrapper)
          );
          const txHash = await web3Wrapper.sendTransactionAsync(
            txDataWithDefaults
          );
          logUtils.log(`transactionHash: ${txHash}`);
          const {
            contractAddress,
          } = await web3Wrapper.awaitTransactionSuccessAsync(txHash);
          logUtils.log(
            `${libraryArtifact.contractName} successfully deployed at ${contractAddress}`
          );
          libraryAddresses[
            libraryArtifact.contractName
          ] = contractAddress as string;
        }
      }
    }
    return libraryAddresses;
  }

  public getFunctionSignature(methodName: string): string {
    const index = this._methodABIIndex[methodName];
    const methodAbi = MultipleMerkleTreesControllerSHAContract.ABI()[
      index
    ] as MethodAbi; // tslint:disable-line:no-unnecessary-type-assertion
    const functionSignature = methodAbiToFunctionSignature(methodAbi);
    return functionSignature;
  }

  public getABIDecodedTransactionData<T>(
    methodName: string,
    callData: string
  ): T {
    const functionSignature = this.getFunctionSignature(methodName);
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    const abiEncoder = self._lookupAbiEncoder(functionSignature);
    const abiDecodedCallData = abiEncoder.strictDecode<T>(callData);
    return abiDecodedCallData;
  }

  public getABIDecodedReturnData<T>(methodName: string, callData: string): T {
    const functionSignature = this.getFunctionSignature(methodName);
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    const abiEncoder = self._lookupAbiEncoder(functionSignature);
    const abiDecodedCallData = abiEncoder.strictDecodeReturnValue<T>(callData);
    return abiDecodedCallData;
  }

  public getSelector(methodName: string): string {
    const functionSignature = this.getFunctionSignature(methodName);
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    const abiEncoder = self._lookupAbiEncoder(functionSignature);
    return abiEncoder.getSelector();
  }

  public latestRoot(index_0: BigNumber): ContractFunctionObj<string> {
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    assert.isBigNumber("index_0", index_0);
    const functionSignature = "latestRoot(uint256)";

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam
      ): Promise<string> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(
          rawCallResult,
          abiEncoder
        );
        return abiEncoder.strictDecodeReturnValue<string>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [index_0]);
      },
    };
  }
  public treeHeight_a(): ContractFunctionObj<BigNumber> {
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    const functionSignature = "treeHeight_a()";

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam
      ): Promise<BigNumber> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(
          rawCallResult,
          abiEncoder
        );
        return abiEncoder.strictDecodeReturnValue<BigNumber>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, []);
      },
    };
  }
  public treeHeight_b(): ContractFunctionObj<BigNumber> {
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    const functionSignature = "treeHeight_b()";

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam
      ): Promise<BigNumber> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(
          rawCallResult,
          abiEncoder
        );
        return abiEncoder.strictDecodeReturnValue<BigNumber>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, []);
      },
    };
  }
  public insertLeaf(
    leafValue: string,
    tree: BigNumber
  ): ContractTxFunctionObj<string> {
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    assert.isString("leafValue", leafValue);
    assert.isBigNumber("tree", tree);
    const functionSignature = "insertLeaf(bytes32,uint256)";

    return {
      async sendTransactionAsync(
        txData?: Partial<TxData> | undefined,
        opts: SendTransactionOpts = { shouldValidate: true }
      ): Promise<string> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync(
          { data: this.getABIEncodedTransactionData(), ...txData },
          this.estimateGasAsync.bind(this)
        );
        if (opts.shouldValidate !== false) {
          await this.callAsync(txDataWithDefaults);
        }
        return self._web3Wrapper.sendTransactionAsync(txDataWithDefaults);
      },
      awaitTransactionSuccessAsync(
        txData?: Partial<TxData>,
        opts: AwaitTransactionSuccessOpts = { shouldValidate: true }
      ): PromiseWithTransactionHash<TransactionReceiptWithDecodedLogs> {
        return self._promiseWithTransactionHash(
          this.sendTransactionAsync(txData, opts),
          opts
        );
      },
      async estimateGasAsync(
        txData?: Partial<TxData> | undefined
      ): Promise<number> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync({
          data: this.getABIEncodedTransactionData(),
          ...txData,
        });
        return self._web3Wrapper.estimateGasAsync(txDataWithDefaults);
      },
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam
      ): Promise<string> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(
          rawCallResult,
          abiEncoder
        );
        return abiEncoder.strictDecodeReturnValue<string>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [
          leafValue,
          tree,
        ]);
      },
    };
  }
  public owner(): ContractFunctionObj<string> {
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    const functionSignature = "owner()";

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam
      ): Promise<string> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(
          rawCallResult,
          abiEncoder
        );
        return abiEncoder.strictDecodeReturnValue<string>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, []);
      },
    };
  }
  public roots(index_0: string): ContractFunctionObj<string> {
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    assert.isString("index_0", index_0);
    const functionSignature = "roots(bytes32)";

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam
      ): Promise<string> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(
          rawCallResult,
          abiEncoder
        );
        return abiEncoder.strictDecodeReturnValue<string>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [index_0]);
      },
    };
  }
  public insertLeaves(
    leafValues: string[],
    tree: BigNumber
  ): ContractTxFunctionObj<string> {
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    assert.isArray("leafValues", leafValues);
    assert.isBigNumber("tree", tree);
    const functionSignature = "insertLeaves(bytes32[],uint256)";

    return {
      async sendTransactionAsync(
        txData?: Partial<TxData> | undefined,
        opts: SendTransactionOpts = { shouldValidate: true }
      ): Promise<string> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync(
          { data: this.getABIEncodedTransactionData(), ...txData },
          this.estimateGasAsync.bind(this)
        );
        if (opts.shouldValidate !== false) {
          await this.callAsync(txDataWithDefaults);
        }
        return self._web3Wrapper.sendTransactionAsync(txDataWithDefaults);
      },
      awaitTransactionSuccessAsync(
        txData?: Partial<TxData>,
        opts: AwaitTransactionSuccessOpts = { shouldValidate: true }
      ): PromiseWithTransactionHash<TransactionReceiptWithDecodedLogs> {
        return self._promiseWithTransactionHash(
          this.sendTransactionAsync(txData, opts),
          opts
        );
      },
      async estimateGasAsync(
        txData?: Partial<TxData> | undefined
      ): Promise<number> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync({
          data: this.getABIEncodedTransactionData(),
          ...txData,
        });
        return self._web3Wrapper.estimateGasAsync(txDataWithDefaults);
      },
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam
      ): Promise<string> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(
          rawCallResult,
          abiEncoder
        );
        return abiEncoder.strictDecodeReturnValue<string>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [
          leafValues,
          tree,
        ]);
      },
    };
  }
  public leafCount(index_0: BigNumber): ContractFunctionObj<BigNumber> {
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    assert.isBigNumber("index_0", index_0);
    const functionSignature = "leafCount(uint256)";

    return {
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam
      ): Promise<BigNumber> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(
          rawCallResult,
          abiEncoder
        );
        return abiEncoder.strictDecodeReturnValue<BigNumber>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [index_0]);
      },
    };
  }
  public _insertLeaf(
    leafValue: string,
    tree: BigNumber
  ): ContractTxFunctionObj<void> {
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    assert.isString("leafValue", leafValue);
    assert.isBigNumber("tree", tree);
    const functionSignature = "_insertLeaf(bytes32,uint256)";

    return {
      async sendTransactionAsync(
        txData?: Partial<TxData> | undefined,
        opts: SendTransactionOpts = { shouldValidate: true }
      ): Promise<string> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync(
          { data: this.getABIEncodedTransactionData(), ...txData },
          this.estimateGasAsync.bind(this)
        );
        if (opts.shouldValidate !== false) {
          await this.callAsync(txDataWithDefaults);
        }
        return self._web3Wrapper.sendTransactionAsync(txDataWithDefaults);
      },
      awaitTransactionSuccessAsync(
        txData?: Partial<TxData>,
        opts: AwaitTransactionSuccessOpts = { shouldValidate: true }
      ): PromiseWithTransactionHash<TransactionReceiptWithDecodedLogs> {
        return self._promiseWithTransactionHash(
          this.sendTransactionAsync(txData, opts),
          opts
        );
      },
      async estimateGasAsync(
        txData?: Partial<TxData> | undefined
      ): Promise<number> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync({
          data: this.getABIEncodedTransactionData(),
          ...txData,
        });
        return self._web3Wrapper.estimateGasAsync(txDataWithDefaults);
      },
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam
      ): Promise<void> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(
          rawCallResult,
          abiEncoder
        );
        return abiEncoder.strictDecodeReturnValue<void>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [
          leafValue,
          tree,
        ]);
      },
    };
  }
  public _insertLeaves(
    leafValues: string[],
    tree: BigNumber
  ): ContractTxFunctionObj<void> {
    const self = (this as any) as MultipleMerkleTreesControllerSHAContract;
    assert.isArray("leafValues", leafValues);
    assert.isBigNumber("tree", tree);
    const functionSignature = "_insertLeaves(bytes32[],uint256)";

    return {
      async sendTransactionAsync(
        txData?: Partial<TxData> | undefined,
        opts: SendTransactionOpts = { shouldValidate: true }
      ): Promise<string> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync(
          { data: this.getABIEncodedTransactionData(), ...txData },
          this.estimateGasAsync.bind(this)
        );
        if (opts.shouldValidate !== false) {
          await this.callAsync(txDataWithDefaults);
        }
        return self._web3Wrapper.sendTransactionAsync(txDataWithDefaults);
      },
      awaitTransactionSuccessAsync(
        txData?: Partial<TxData>,
        opts: AwaitTransactionSuccessOpts = { shouldValidate: true }
      ): PromiseWithTransactionHash<TransactionReceiptWithDecodedLogs> {
        return self._promiseWithTransactionHash(
          this.sendTransactionAsync(txData, opts),
          opts
        );
      },
      async estimateGasAsync(
        txData?: Partial<TxData> | undefined
      ): Promise<number> {
        const txDataWithDefaults = await self._applyDefaultsToTxDataAsync({
          data: this.getABIEncodedTransactionData(),
          ...txData,
        });
        return self._web3Wrapper.estimateGasAsync(txDataWithDefaults);
      },
      async callAsync(
        callData: Partial<CallData> = {},
        defaultBlock?: BlockParam
      ): Promise<void> {
        BaseContract._assertCallParams(callData, defaultBlock);
        const rawCallResult = await self._performCallAsync(
          { data: this.getABIEncodedTransactionData(), ...callData },
          defaultBlock
        );
        const abiEncoder = self._lookupAbiEncoder(functionSignature);
        BaseContract._throwIfUnexpectedEmptyCallResult(
          rawCallResult,
          abiEncoder
        );
        return abiEncoder.strictDecodeReturnValue<void>(rawCallResult);
      },
      getABIEncodedTransactionData(): string {
        return self._strictEncodeArguments(functionSignature, [
          leafValues,
          tree,
        ]);
      },
    };
  }

  /**
   * Subscribe to an event type emitted by the MultipleMerkleTreesControllerSHA contract.
   * @param eventName The MultipleMerkleTreesControllerSHA contract event you would like to subscribe to.
   * @param indexFilterValues An object where the keys are indexed args returned by the event and
   * the value is the value you are interested in. E.g `{maker: aUserAddressHex}`
   * @param callback Callback that gets called when a log is added/removed
   * @param isVerbose Enable verbose subscription warnings (e.g recoverable network issues encountered)
   * @return Subscription token used later to unsubscribe
   */
  public subscribe<ArgsType extends MultipleMerkleTreesControllerSHAEventArgs>(
    eventName: MultipleMerkleTreesControllerSHAEvents,
    indexFilterValues: IndexedFilterValues,
    callback: EventCallback<ArgsType>,
    isVerbose: boolean = false,
    blockPollingIntervalMs?: number
  ): string {
    assert.doesBelongToStringEnum(
      "eventName",
      eventName,
      MultipleMerkleTreesControllerSHAEvents
    );
    assert.doesConformToSchema(
      "indexFilterValues",
      indexFilterValues,
      schemas.indexFilterValuesSchema
    );
    assert.isFunction("callback", callback);
    const subscriptionToken = this._subscriptionManager.subscribe<ArgsType>(
      this.address,
      eventName,
      indexFilterValues,
      MultipleMerkleTreesControllerSHAContract.ABI(),
      callback,
      isVerbose,
      blockPollingIntervalMs
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
   * @param eventName The MultipleMerkleTreesControllerSHA contract event you would like to subscribe to.
   * @param blockRange Block range to get logs from.
   * @param indexFilterValues An object where the keys are indexed args returned by the event and
   * the value is the value you are interested in. E.g `{_from: aUserAddressHex}`
   * @return Array of logs that match the parameters
   */
  public async getLogsAsync<
    ArgsType extends MultipleMerkleTreesControllerSHAEventArgs
  >(
    eventName: MultipleMerkleTreesControllerSHAEvents,
    blockRange: BlockRange,
    indexFilterValues: IndexedFilterValues
  ): Promise<Array<LogWithDecodedArgs<ArgsType>>> {
    assert.doesBelongToStringEnum(
      "eventName",
      eventName,
      MultipleMerkleTreesControllerSHAEvents
    );
    assert.doesConformToSchema(
      "blockRange",
      blockRange,
      schemas.blockRangeSchema
    );
    assert.doesConformToSchema(
      "indexFilterValues",
      indexFilterValues,
      schemas.indexFilterValuesSchema
    );
    const logs = await this._subscriptionManager.getLogsAsync<ArgsType>(
      this.address,
      eventName,
      blockRange,
      indexFilterValues,
      MultipleMerkleTreesControllerSHAContract.ABI()
    );
    return logs;
  }

  constructor(
    address: string,
    supportedProvider: SupportedProvider,
    txDefaults?: Partial<TxData>,
    logDecodeDependencies?: { [contractName: string]: ContractAbi },
    deployedBytecode:
      | string
      | undefined = MultipleMerkleTreesControllerSHAContract.deployedBytecode
  ) {
    super(
      "MultipleMerkleTreesControllerSHA",
      MultipleMerkleTreesControllerSHAContract.ABI(),
      address,
      supportedProvider,
      txDefaults,
      logDecodeDependencies,
      deployedBytecode
    );
    classUtils.bindAll(this, [
      "_abiEncoderByFunctionSignature",
      "address",
      "_web3Wrapper",
    ]);
    this._subscriptionManager = new SubscriptionManager<
      MultipleMerkleTreesControllerSHAEventArgs,
      MultipleMerkleTreesControllerSHAEvents
    >(MultipleMerkleTreesControllerSHAContract.ABI(), this._web3Wrapper);
    MultipleMerkleTreesControllerSHAContract.ABI().forEach((item, index) => {
      if (item.type === "function") {
        const methodAbi = item as MethodAbi;
        this._methodABIIndex[methodAbi.name] = index;
      }
    });
  }
}

// tslint:disable:max-file-line-count
// tslint:enable:no-unbound-method no-parameter-reassignment no-consecutive-blank-lines ordered-imports align
// tslint:enable:trailing-comma whitespace no-trailing-whitespace
