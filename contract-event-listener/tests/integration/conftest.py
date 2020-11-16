"""
This configuration created with integration testing docker compose environment in mind.
Most probably it will not work with any other environment. Because of this integration tests
will fail. The environment includes: localstack, ganache-cli and special simple event emitter contract.
All of these components must be present in order for tests to work properly.
"""
import os
import copy
import urllib
import boto3
import pytest
from web3 import Web3
from src.config import Config
from src.contract import Contract


WALLET_PUBLIC_KEY = os.environ['WALLET_PUBLIC_KEY']
WALLET_PRIVATE_KEY = os.environ['WALLET_PRIVATE_KEY']

AWS_ENDPOINT_URL = os.environ['AWS_ENDPOINT_URL']

AWS_RESOURCE_CONFIG = dict(
    endpoint_url=AWS_ENDPOINT_URL,
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
)


def queue_url(name):
    return urllib.parse.urljoin(AWS_ENDPOINT_URL, f'000000000000/{name}')


JSON_TRANSFORM = {
    'Event': 'args',
    'Block': 'blockNumber'
}

EVENT_FILTER = {
    'argument_filters': {
        'receiver': 'AU'
    }
}

CONFIG = {
    'Receivers': [
        {
            'Id': 'MessageReceivedSQS',
            'Type': 'SQS',
            'QueueUrl': queue_url('message-received-event'),
            'JSON': JSON_TRANSFORM
        },
        {
            'Id': 'MessageReceivedLOG',
            'Type': 'LOG',
            'JSON': JSON_TRANSFORM
        },
        {
            'Id': 'MessageSentSQS',
            'Type': 'SQS',
            'QueueUrl': queue_url('message-sent-event'),
            'JSON': JSON_TRANSFORM
        },
        {
            'Id': 'MessageSentLOG',
            'Type': 'LOG',
            'JSON': JSON_TRANSFORM
        },
        {
            'Id': 'MessageSQS',
            'Type': 'SQS',
            'QueueUrl': queue_url('message-event'),
            'JSON': JSON_TRANSFORM
        },
        {
            'Id': 'MessageLOG',
            'Type': 'LOG',
            'JSON': JSON_TRANSFORM
        }
    ],
    'Listeners': [
        {
            'Id': 'MessageReceived',
            'Event': {
                'Name': 'MessageReceived',
                'Filter': EVENT_FILTER
            },
            'Receivers': [
                'MessageReceivedSQS',
                'MessageReceivedLOG',
                'MessageSQS',
                'MessageLOG'
            ]
        },
        {
            'Id': 'MessageSent',
            'Event': {
                'Name': 'MessageSent',
                'Filter': EVENT_FILTER
            },
            'Receivers': [
                'MessageSentSQS',
                'MessageSentLOG',
                'MessageSQS',
                'MessageLOG'
            ]
        }
    ],
    'Worker': {
        'Blockchain': {
            'URI': 'ws://baseline-ganache-cli:8585'
        },
        'General': {
            'PollingInterval': 10,
            'ListenerBlocksLogDir': '/tmp/listener-blocks-log',
            'LoggerName': 'DEV'
        },
        'Contract': {
            'S3': {
                'Bucket': 'contract',
                'Key': 'event-emitter/EventEmitter.json',
                'NetworkId': '15'
            }
        }
    }
}


@pytest.fixture(scope='function')
def worker_config_json():
    return copy.deepcopy(CONFIG)


@pytest.fixture(scope='session')
def worker_config():
    # Config.load returns namedtuple
    return Config().load(CONFIG)


@pytest.fixture(scope='session')
def web3():
    config = Config().load(CONFIG)
    web3 = Web3(Web3.WebsocketProvider(config.Worker.Blockchain.URI))
    yield web3


@pytest.fixture(scope='function')
def latest_block(web3):
    def value():
        return web3.eth.blockNumber
    return value


@pytest.fixture(scope='session')
def contract(web3):
    config = Config().load(CONFIG)
    yield Contract(web3, config.Worker.Contract)


@pytest.fixture(scope='function')
def empty_queue():
    client = boto3.client('sqs', **AWS_RESOURCE_CONFIG)

    def get_empty_queue(name):
        url = queue_url(name)
        client.purge_queue(QueueUrl=url)
        return boto3.resource('sqs', **AWS_RESOURCE_CONFIG).Queue(url)

    yield get_empty_queue


@pytest.fixture(scope='session')
def emit(web3, contract):
    def emitEvent(name, receiver, text):
        transaction = {
            'from': WALLET_PUBLIC_KEY,
            'nonce': web3.eth.getTransactionCount(WALLET_PUBLIC_KEY, 'pending')
        }
        unsigned_transaction = contract.functions.emitEvent(name, receiver, text).buildTransaction(transaction)
        signed_transaction = web3.eth.account.sign_transaction(
            unsigned_transaction,
            private_key=WALLET_PRIVATE_KEY
        )
        tx_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        return web3.eth.waitForTransactionReceipt(tx_hash, 180)
    yield emitEvent


@pytest.fixture(scope='session')
def MessageReceived(emit):
    def Event(receiver, text):
        emit('MessageReceived', receiver, text)
    yield Event


@pytest.fixture(scope='session')
def MessageSent(emit):
    def Event(receiver, text):
        emit('MessageSent', receiver, text)
    yield Event
