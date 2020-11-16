
# build/abi/MerkleTreeSHA.json
abigen --pkg baseline build/abi/MerkleTreeSHA.json > MerkleTreeSHA.js
abi-gen --abis 'build/abi/**/*.json' --out 'output/generated/'
