import json
import web3
from libtrustbridge.repos.miniorepo import MinioRepo


def Contract(
    web3: web3.Web3 = None,
    repo: MinioRepo = None,
    network_id: str = None,
    artifact_key: str = None
) -> web3.eth.Contract:
    artifact = json.loads(repo.get_object_content(artifact_key))
    return web3.eth.contract(address=artifact['networks'][network_id]['address'], abi=artifact['abi'])
