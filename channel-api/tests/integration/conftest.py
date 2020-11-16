import pytest
from http import HTTPStatus
import urllib
import requests
from src import repos
from libtrustbridge.utils.conf import env_s3_config, env_queue_config, env


NOTIFICATIONS_REPO = env_queue_config('NOTIFICATIONS_REPO')
DELIVERY_OUTBOX_REPO = env_queue_config('DELIVERY_OUTBOX_REPO')
SUBSCRIPTIONS_REPO = env_s3_config('SUBSCRIPTIONS_REPO')
CHANNEL_REPO = env_queue_config('CHANNEL_REPO')
ENDPOINT = env('ENDPOINT', default='AU')


@pytest.fixture(scope='function')
def notifications_repo():
    repo = repos.Notifications(NOTIFICATIONS_REPO)
    repo.WAIT_FOR_MESSAGE_SECONDS = 1
    repo._unsafe_method__clear()
    yield repo


@pytest.fixture(scope='function')
def delivery_outbox_repo():
    repo = repos.DeliveryOutbox(DELIVERY_OUTBOX_REPO)
    repo.WAIT_FOR_MESSAGE_SECONDS = 1
    repo._unsafe_method__clear()
    yield repo


@pytest.fixture(scope='function')
def subscriptions_repo():
    repo = repos.Subscriptions(SUBSCRIPTIONS_REPO)
    repo._unsafe_method__clear()
    yield repo


@pytest.fixture(scope='function')
def channel_repo():
    repo = repos.Channel(CHANNEL_REPO)
    repo.WAIT_FOR_MESSAGE_SECONDS = 1
    repo._unsafe_method__clear()
    yield repo


class CallbackServer:

    def __init__(self, base_url=None):
        self.base_url = base_url if base_url.endswith('/') else base_url + '/'

    def get_callback_record(self, index):
        url = urllib.parse.urljoin(self.base_url, f'callbacks/{index}')
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return None
        else:
            raise Exception(f'Unexpected response:{response.status_code}')

    def get_callback_records(self):
        url = urllib.parse.urljoin(self.base_url, 'callbacks')
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            raise Exception(f'Unexpected response:{response.status_code}')

    def clear_callback_records(self):
        url = urllib.parse.urljoin(self.base_url, 'callbacks')
        response = requests.delete(url)
        if response.status_code == HTTPStatus.OK:
            pass
        else:
            raise Exception(f'Unexpected response:{response.status_code}')

    def valid_callback_url(self, id):
        return urllib.parse.urljoin(self.base_url, f'callback/valid/{id}')

    def invalid_callback_url(self, id):
        return urllib.parse.urljoin(self.base_url, f'callback/invalid/{id}')


@pytest.fixture(scope='function')
def callback_server():
    callback_server = CallbackServer('http://baseline-channel-api-callback-server:11001')
    callback_server.clear_callback_records()
    yield callback_server
