import urllib
import time
from http import HTTPStatus
from src.processors.callback_delivery import CallbackDelivery
from src.processors.use_cases import DeliverCallbackUseCase
from src.processors.callback_delivery.config import Config


def test(delivery_outbox_repo, callback_server):
    config = Config()
    processor = CallbackDelivery(config)

    # preparing topic and expected topic self link
    topic = 'jurisdiction.AU'
    topic_self_link_base = (
        config.TOPIC_BASE_SELF_URL
        if config.TOPIC_BASE_SELF_URL.endswith('/')
        else config.TOPIC_BASE_SELF_URL + '/'
    )
    expected_topic_self_link = urllib.parse.urljoin(topic_self_link_base, topic)
    assert expected_topic_self_link == '/topic/jurisdiction.AU'

    expected_request_header = {
        'Link': f'<{config.CHANNEL_URL}>; rel="hub", <{expected_topic_self_link}>; rel="self"'
    }

    job = {
        's': None,
        'payload': {
            'id': 'transaction-hash'
        },
        'topic': topic
    }

    subscribers = [
        callback_server.valid_callback_url(1),
        callback_server.valid_callback_url(2),
        callback_server.invalid_callback_url(3)
    ]
    # empty delivery_outbox_repo, processor must do nothing
    next(processor)
    assert not callback_server.get_callback_records()

    # the delivery outbox repo contains two jobs, must send jobs paylod to specified subscribers
    for url in subscribers:
        delivery_outbox_repo.post_job({**job, 's': url})

    for i in range(2):
        next(processor)
        callback_record = callback_server.get_callback_record(-1)
        assert callback_record
        assert callback_record['id'] == str(i + 1)
        assert callback_record['status_code'] == HTTPStatus.OK
        assert callback_record['headers']['Link'] == expected_request_header['Link']
    callback_server.clear_callback_records()
    processor.use_case.MAX_RETRY_TIME = 5
    for i in range(DeliverCallbackUseCase.MAX_ATTEMPTS):
        next(processor)
        time.sleep(processor.use_case._last_retry_time)
    callback_records = callback_server.get_callback_records()
    assert len(callback_records) == DeliverCallbackUseCase.MAX_ATTEMPTS
