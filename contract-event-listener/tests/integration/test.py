import os
from collections import namedtuple
from contextlib import contextmanager
import time
import tempfile
import json
import yaml
import pytest
from src.config import Config
from src.worker import Worker
from src.contract import Contract
from src.loggers import logging
from tests.integration.conftest import CONFIG


logger = logging.getLogger('TEST')


def test_worker(empty_queue, MessageSent, MessageReceived, latest_block, worker_config_json):

    def queue_messages(queue):
        received_messages = []
        while new_messages := queue.receive_messages(
            WaitTimeSeconds=1,
            MaxNumberOfMessages=1
        ):  # noqa
            received_messages.append(json.loads(new_messages[0].body))
        received_messages.sort(key=lambda e: e['Block'])
        return [m['Event'] for m in received_messages]

    @contextmanager
    def wait_for_blocks(number):
        logger.info('Waiting for %s blocks to be mined...', number)
        target = latest_block() + number
        yield target
        while latest_block() < target:
            time.sleep(1)
        logger.info('Blocks mined')

    # making temporary directory for each test run to prevent picking previos block logs
    worker_config_json['Worker']['General']['ListenerBlocksLogDir'] = tempfile.mkdtemp()

    # configuration with no from block set, worker should pick from blocks from blocks log
    no_from_block_config = Config().load(worker_config_json)
    # modifying Listener.Event.Filter.fromBlock to not receive older messages
    for listener in worker_config_json['Listeners']:
        listener['Event']['Filter']['fromBlock'] = latest_block() + 1

    latest_from_block_config = Config().load(worker_config_json)
    worker = Worker(latest_from_block_config)

    # preparing queues
    message_received_event_queue = empty_queue('message-received-event')
    message_sent_event_queue = empty_queue('message-sent-event')
    message_event_queue = empty_queue('message-event')

    message_sent_event = {'receiver': 'AU', 'text': '1'}
    message_received_event = {'receiver': 'AU', 'text': '2'}

    # emitting two events
    with wait_for_blocks(2):
        MessageSent(message_sent_event['receiver'], message_sent_event['text'])
        MessageReceived(message_received_event['receiver'], message_received_event['text'])

    # poll method should pick them all and send them to the corresponding receivers
    worker.poll()

    # both events should go into general message queue
    messages = queue_messages(message_event_queue)
    assert messages == [message_sent_event, message_received_event]

    # and each event type should go into the corresponding queue
    messages = queue_messages(message_received_event_queue)
    assert messages == [message_received_event]

    messages = queue_messages(message_sent_event_queue)
    assert messages == [message_sent_event]

    # clearing queues
    message_received_event_queue = empty_queue('message-received-event')
    message_sent_event_queue = empty_queue('message-sent-event')
    message_event_queue = empty_queue('message-event')

    # these events should be ignored due to the filter configuration {'receiver': 'AU'}
    with wait_for_blocks(2):
        MessageSent('GB', 'Ignored')
        MessageReceived('GB', 'Ignored')

    worker.poll()

    assert not queue_messages(message_sent_event_queue)
    assert not queue_messages(message_received_event_queue)
    assert not queue_messages(message_event_queue)

    # Testing listener blocks log functionality that restores listener last seen block as its
    # initial filter fromBlock. It allows listening for events missed during inactivity periods.
    # This may happen due to a variety of reasons. Primarily baselinehnical issues.
    # The logs are stored on a filesystem in a specified directory that supposedly located inside
    # a remote volume to persist data between launches.

    message_sent_event['text'] = 'Test blocks log'
    message_received_event['text'] = 'Test blocks log'
    with wait_for_blocks(2):
        MessageSent(message_sent_event['receiver'], message_sent_event['text'])
        MessageReceived(message_received_event['receiver'], message_received_event['text'])
    # recreating worker without fromBlock set manually, should pick the values from files
    worker = Worker(no_from_block_config)

    worker.poll()

    # both events should go into general message queue
    messages = queue_messages(message_event_queue)
    assert messages == [message_sent_event, message_received_event]

    # and each event type should go into the corresponding queue
    messages = queue_messages(message_received_event_queue)
    assert messages == [message_received_event]

    messages = queue_messages(message_sent_event_queue)
    assert messages == [message_sent_event]


def test_config_from_file():
    with tempfile.TemporaryDirectory() as tmp_dir:

        json_config_invalid_ext_filename = os.path.join(tmp_dir, 'config.js')
        json_config_no_ext_filename = os.path.join(tmp_dir, 'config')
        json_conf_filename = os.path.join(tmp_dir, 'config.json')
        yaml_conf_filename = os.path.join(tmp_dir, 'config.yaml')

        # file is not created yet, must throw FileNotFoundError
        with pytest.raises(FileNotFoundError):
            Config.from_file(json_conf_filename)

        # writing files
        with open(json_conf_filename, 'wt+') as f:
            json.dump(CONFIG, f)

        with open(json_config_no_ext_filename, 'wt+') as f:
            json.dump(CONFIG, f)

        with open(json_config_invalid_ext_filename, 'wt+') as f:
            json.dump(CONFIG, f)

        with open(yaml_conf_filename, 'wt+') as f:
            yaml.dump(CONFIG, f, Dumper=yaml.dumper.SafeDumper)

        # unsupported extension
        with pytest.raises(ValueError) as einfo:
            Config.from_file(json_config_invalid_ext_filename)
        assert str(einfo.value) == 'Unsupported config file extension ".js"'

        # no extension
        with pytest.raises(ValueError) as einfo:
            Config.from_file(json_config_no_ext_filename)
        assert str(einfo.value) == 'Unsupported config file extension ""'

        # config files loading equivalency
        assert Config.from_file(json_conf_filename) == Config.from_file(yaml_conf_filename) == Config().load(CONFIG)


def test_contract_loading(worker_config_json, web3):
    config = Config().load(worker_config_json)

    # default config uses s3
    assert config.Worker.Contract.S3.Bucket and config.Worker.Contract.S3.Key and config.Worker.Contract.S3.NetworkId
    # testing S3 Loading
    s3_contract = Contract(web3, config.Worker.Contract)

    # testing File Loading
    with tempfile.TemporaryDirectory() as tmp_dir:
        del worker_config_json['Worker']['Contract']['S3']
        address_filename = os.path.join(tmp_dir, 'contract.address')
        abi_filename = os.path.join(tmp_dir, 'abi.json')
        worker_config_json['Worker']['Contract']['File'] = {
            'Address': address_filename,
            'ABI': abi_filename
        }
        with open(address_filename, 'wt+') as f:
            f.write(s3_contract.address)
        with open(abi_filename, 'wt+') as f:
            # ABI file must be json with {'abi':[...]} structure
            f.write(json.dumps({'abi': s3_contract.abi}))
        config = Config().load(worker_config_json)
        file_contract = Contract(web3, config.Worker.Contract)

    # must be equivalent
    assert file_contract.abi == s3_contract.abi
    assert file_contract.address == s3_contract.address

    # both options missing must raise ValueError
    ContractConfig = namedtuple('Config', ['S3', 'File'])
    with pytest.raises(ValueError) as einfo:
        Contract(web3, ContractConfig(None, None))
    assert str(einfo.value) == 'Contract config.File and config.S3 sections are undefined'
