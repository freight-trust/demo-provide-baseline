import os
import time
import json
import logging
from http import HTTPStatus
import urllib
import pytest
import requests

CHANNEL_API_B_URL = os.environ['CHANNEL_API_B_URL']
CHANNEL_API_B_SENDER = os.environ['CHANNEL_API_B_SENDER']

CHANNEL_API_A_URL = os.environ['CHANNEL_API_A_URL']
CHANNEL_API_A_SENDER = os.environ['CHANNEL_API_A_SENDER']

CALLBACK_SERVER_URL = os.environ['CALLBACK_SERVER_URL']

logging.basicConfig(level=logging.DEBUG)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger('SYSTEM_TEST')


class ChannelAPI:

    def __init__(self, base_url, sender):
        self.base_url = base_url
        self.sender = sender
        self.logger = logging.getLogger(urllib.parse.urlparse(base_url).netloc)

    def get_participants(self):
        self.logger.debug('get_participants')
        url = urllib.parse.urljoin(self.base_url, 'participants')
        return requests.get(url)

    def get_message(self, id):
        self.logger.debug('get_message(%s)', id)
        url = urllib.parse.urljoin(self.base_url, f'messages/{id}')
        return requests.get(url)

    def get_topic_url(self, topic):
        self.logger.debug('get_topic_url(%s)', topic)
        return urllib.parse.urljoin(self.base_url, f'topic/{topic}')

    def get_topic(self, topic):
        self.logger.debug('get_topic(%s)', topic)
        url = urllib.parse.urljoin(self.base_url, f'topic/{topic}')
        return requests.get(url)

    def post_message(self, data):
        self.logger.debug('post_message(data)')
        self.logger.debug(json.dumps(data, indent=4))
        url = urllib.parse.urljoin(self.base_url, 'messages')
        return requests.post(url, json=data)

    def post_subscription_by_id(self, data):
        self.logger.debug('post_subscription_by_id(data)')
        self.logger.debug(json.dumps(data, indent=4))
        url = urllib.parse.urljoin(self.base_url, 'messages/subscriptions/by_id')
        return requests.post(url, data=data)

    def post_subscription_by_jurisdiction(self, data):
        self.logger.debug('post_subscription_by_jurisdiction(data)')
        self.logger.debug(json.dumps(data, indent=4))
        url = urllib.parse.urljoin(self.base_url, 'messages/subscriptions/by_jurisdiction')
        return requests.post(url, data=data)


@pytest.fixture(scope='function')
def channel_api_b():
    yield ChannelAPI(CHANNEL_API_B_URL, CHANNEL_API_B_SENDER)


@pytest.fixture(scope='function')
def channel_api_a():
    yield ChannelAPI(CHANNEL_API_A_URL, CHANNEL_API_A_SENDER)


class CallbackServer:

    def __init__(self, base_url=None):
        self.base_url = base_url
        self.logger = logging.getLogger(urllib.parse.urlparse(base_url).netloc)

    def get_callback_record(self, index):
        logger.debug('get_callback_record(%s)', index)
        url = urllib.parse.urljoin(self.base_url, f'callbacks/{index}')
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return None
        else:
            raise Exception(f'Unexpected response:{response.status_code}')

    def __get_callback_records(self, id=None):
        url = urllib.parse.urljoin(self.base_url, 'callbacks')
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            records = response.json()
            if id is not None:
                return [record for record in records if record['id'] == id]
            else:
                return records
        else:
            raise Exception(f'Unexpected response:{response.status_code}')

    def get_callback_records(self, id=None, attemps=1, interval=1, delay=0):
        self.logger.debug('get_callback_record(id=%s,attemps=%s, interval=%s,delay=%s)', id, attemps, interval, delay)
        attemps = max(attemps, 1)
        delay = max(delay, 0)
        if delay > 0:
            time.sleep(delay)
        for i in range(attemps):
            self.logger.debug('attempt %s', i + 1)
            records = self.__get_callback_records(id=id)
            if records:
                return records
            else:
                time.sleep(interval)
        return []

    def clear_callback_records(self):
        self.logger.debug('clear_callback_records')
        url = urllib.parse.urljoin(self.base_url, 'callbacks')
        response = requests.delete(url)
        if response.status_code == HTTPStatus.OK:
            pass
        else:
            raise Exception(f'Unexpected response:{response.status_code}')

    def valid_callback_url(self, id):
        self.logger.debug('valid_callback_url(%s)', id)
        return urllib.parse.urljoin(self.base_url, f'callback/valid/{id}')

    def invalid_callback_url(self, id):
        self.logger.debug('invalid_callback_url(%s)', id)
        return urllib.parse.urljoin(self.base_url, f'callback/invalid/{id}')


@pytest.fixture(scope='function')
def callback_server():
    callback_server = CallbackServer(CALLBACK_SERVER_URL)
    callback_server.clear_callback_records()
    yield callback_server
