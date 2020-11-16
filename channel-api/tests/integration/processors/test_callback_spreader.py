from libtrustbridge.websub.domain import Pattern
from src.processors.callback_spreader import CallbackSpreader
from src.processors.callback_spreader.config import Config


def test(notifications_repo, delivery_outbox_repo, subscriptions_repo):

    config = Config()
    processor = CallbackSpreader(config)

    subscribers = [
        'subscriber/1',
        'subscriber/2'
    ]
    topic = 'aaa.bbb'
    job = {
        'topic': topic,
        'content': {
            'id': 'transaction-hash'
        }
    }

    # creating test subscriptions
    assert subscriptions_repo.is_empty()
    for url in subscribers:
        subscriptions_repo.subscribe_by_pattern(Pattern(topic), url, 300000)

    # empty notifications_repo, processor must do nothing
    assert notifications_repo.is_empty()
    assert delivery_outbox_repo.is_empty()

    next(processor)
    assert notifications_repo.is_empty()
    assert delivery_outbox_repo.is_empty()

    # processor must pick the job from notifications repo
    # with matching topic and create delivery job for each subscription

    notifications_repo.post_job(job)
    next(processor)

    # checking delivery jobs
    for i in range(2):
        queue_job = delivery_outbox_repo.get_job()
        assert queue_job
        queue_msg_id, queue_job = queue_job
        assert queue_job['s'] in subscribers
        assert queue_job['payload'] == job['content']
        assert queue_job['topic'] == topic
    # checking that all delivery jobs tested
    assert not delivery_outbox_repo.get_job()
    # checking that notifications repo job was deleted after succesfully processing
    assert notifications_repo.is_empty()

    # this topic has no subscriptions, processor must not create delivery jobs
    topic = 'aaa.ddd'
    job = {
        'topic': topic,
        'content': {
            'id': 'transaction-hash'
        }
    }

    notifications_repo.post_job(job)
    next(processor)
    # checking that no delivery jobs were created
    assert delivery_outbox_repo.is_empty()
    # checking that notifications repo job was deleted after succesfully processing
    assert notifications_repo.is_empty()
