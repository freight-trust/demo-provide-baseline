import json
from src import aws


def Contract(web3, config):
    if config.S3:
        s3 = aws.s3()
        bucket = s3.Bucket(config.S3.Bucket)
        artifact = json.load(bucket.Object(config.S3.Key).get()['Body'])
        address = artifact['networks'][config.S3.NetworkId]['address']
        abi = artifact['abi']
    elif config.File:
        with open(config.File.Address, 'rt') as f:
            address = f.read()
        with open(config.File.ABI, 'rt') as f:
            abi = json.load(f)['abi']
    else:
        raise ValueError("Contract config.File and config.S3 sections are undefined")
    return web3.eth.contract(address=address, abi=abi)
