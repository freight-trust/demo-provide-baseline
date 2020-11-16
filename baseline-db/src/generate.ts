import {
  generateContractInterfaces,
  CompilerOutput,
} from "@zoltu/solidity-typescript-generator";
import { promises as filesystem } from "fs";
import * as path from "path";
import { abi } from "./abi";
import { ensureDirectoryExists } from "./utils";

const generatedFileName = "my-token";
const solidityFileName = "erc20.sol";
const contractName = "Erc20";

async function writeGeneratedInterface(compilerOutput: CompilerOutput) {
  const filePath = path.join(__dirname, "generated", `${generatedFileName}.ts`);
  await ensureDirectoryExists(path.dirname(filePath));
  const fileContents = await generateContractInterfaces(compilerOutput);
  await filesystem.writeFile(filePath, fileContents, {
    encoding: "utf8",
    flag: "w",
  });
}

async function main() {
  const compilerOutput = {
    contracts: { [solidityFileName]: { [contractName]: { abi } } },
  };
  await writeGeneratedInterface(compilerOutput);
}

main()
  .then(() => {
    process.exit(0);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
