from src.processors.new_messages_observer import NewMessagesObserver
from src.processors.new_messages_observer.config import Config


def test(notifications_repo, channel_repo):

    config = Config()
    processor = NewMessagesObserver(config)
    message = {
        'id': 'transaction hash',
        'message': {
            'receiver': config.RECEIVER
        }
    }
    # empty repos, processor should do nothing
    assert notifications_repo.is_empty()
    assert channel_repo.is_empty()
    next(processor)
    assert notifications_repo.is_empty()
    assert channel_repo.is_empty()
    # a job posted to the channel repo, the processor must post a job to the notifications repo
    channel_repo.post_job(message)
    next(processor)
    # a channel repo message must be deleted after the successful processing
    assert not channel_repo.get_job()
    queue_message = notifications_repo.get_job()
    queue_message_id, queue_job = queue_message
    assert queue_job == {
        'topic': f'jurisdiction.{message["message"]["receiver"]}',
        'content': {
            'id': message['id']
        }
    }
    # invalid message receiver, job must be ignored, but deleted from the channel_repo
    notifications_repo._unsafe_method__clear()
    channel_repo._unsafe_method__clear()
    message = {
        'id': 'transaction hash',
        'message': {
            'receiver': 'GB'
        }
    }
    channel_repo.post_job(message)
    next(processor)
    # after successful processing all repos must remain empty
    assert notifications_repo.is_empty()
    assert channel_repo.is_empty()
