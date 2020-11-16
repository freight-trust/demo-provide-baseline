from unittest import mock
from http import HTTPStatus
import requests
from src.processors import use_cases


def test_NewMessageNotifyUseCase():
    receiver = 'AU'
    channel_repo = mock.MagicMock()
    notifications_repo = mock.MagicMock()

    use_case = use_cases.NewMessagesNotifyUseCase(
        receiver=receiver,
        channel_repo=channel_repo,
        notifications_repo=notifications_repo
    )
    # no new messages, use case does nothing
    channel_repo.get_job.return_value = None
    assert not use_case.execute()
    # correct message receiver
    queue_message_id = 'queue_message_id'
    message_id = 'transaction_hash'
    message = {
        'id': message_id,
        'message': {
            'receiver': receiver
        }
    }
    channel_repo.get_job.return_value = (queue_message_id, message)
    assert use_case.execute()
    channel_repo.delete.assert_called_once_with(queue_message_id)
    notifications_repo.post_job.assert_called_once_with({
        'topic': f'jurisdiction.{receiver}',
        'content': {
            'id': message_id
        }
    })
    # incorrect message receiver
    channel_repo.reset_mock()
    notifications_repo.reset_mock()
    message['message']['receiver'] = 'GB'
    assert not use_case.execute()
    notifications_repo.post_job.assert_not_called()


def test_DispatchMessageToSubscribersUseCase():
    notifications_repo = mock.MagicMock()
    delivery_outbox_repo = mock.MagicMock()
    subscriptions_repo = mock.MagicMock()
    subscription = mock.MagicMock()

    use_case = use_cases.DispatchMessageToSubscribersUseCase(
        notifications_repo=notifications_repo,
        subscriptions_repo=subscriptions_repo,
        delivery_outbox_repo=delivery_outbox_repo
    )

    # no jobs in notifications repo, use_case must do nothing
    notifications_repo.get_job.return_value = None
    assert not use_case.execute()
    notifications_repo.get_job.assert_called_once()
    # notifications repo has job, but there are no matching subscriptions to notify
    notifications_repo.reset_mock()
    subscriptions_repo.reset_mock()
    delivery_outbox_repo.reset_mock()
    queue_message_id = 'queue_message_id'
    message = {
        'topic': 'jurisdiction.AU',
        'content': {
            'id': 'transaction_hash'
        }
    }
    notifications_repo.get_job.return_value = (queue_message_id, message)
    subscriptions_repo.get_subscriptions_by_pattern.return_value = []
    use_case.execute()
    notifications_repo.get_job.assert_called_once()
    subscriptions_repo.get_subscriptions_by_pattern.assert_called_once()
    delivery_outbox_repo.post_job.assert_not_called()

    # notifications repo has job, but there are no valid subscriptions to notify
    notifications_repo.reset_mock()
    subscriptions_repo.reset_mock()
    delivery_outbox_repo.reset_mock()
    queue_message_id = 'queue_message_id'
    message = {
        'topic': 'jurisdiction.AU',
        'content': {
            'id': 'transaction_hash'
        }
    }
    notifications_repo.get_job.return_value = (queue_message_id, message)
    subscription.is_valid = False
    subscriptions_repo.get_subscriptions_by_pattern.return_value = [subscription]
    use_case.execute()
    notifications_repo.get_job.assert_called_once()
    subscriptions_repo.get_subscriptions_by_pattern.assert_called_once()
    delivery_outbox_repo.post_job.assert_not_called()

    # notifications repo has job and there is a subscription to notify
    notifications_repo.reset_mock()
    subscriptions_repo.reset_mock()
    delivery_outbox_repo.reset_mock()
    queue_message_id = 'queue_message_id'
    message = {
        'topic': 'jurisdiction.AU',
        'content': {
            'id': 'transaction_hash'
        }
    }
    notifications_repo.get_job.return_value = (queue_message_id, message)
    subscription.is_valid = True
    subscriptions_repo.get_subscriptions_by_pattern.return_value = [subscription]
    use_case.execute()
    notifications_repo.get_job.assert_called_once()
    subscriptions_repo.get_subscriptions_by_pattern.assert_called_once()
    delivery_outbox_repo.post_job.assert_called_once_with({
        's': subscription.callback_url,
        'topic': message['topic'],
        'payload': message['content']
    })


@mock.patch('src.processors.use_cases.requests.post')
def test_DeliverCallbackUseCase(post):
    delivery_outbox_repo = mock.MagicMock()
    channel_url = 'http://channel.api.example'
    topic_base_self_url = 'topic'
    topic = 'a.b.c'
    callback = 'http://callback.examle/callback'

    response = mock.MagicMock()
    post.return_value = response

    payload = {
        'receiver': 'AU',
        'obj': 'object'
    }

    use_case = use_cases.DeliverCallbackUseCase(
        delivery_outbox_repo=delivery_outbox_repo,
        channel_url=channel_url,
        topic_base_self_url=topic_base_self_url
    )

    queue_message_id = 'queue_message_id'
    message = {
        's': callback,
        'topic': topic,
        'payload': payload
    }

    headers = {
        'Link': f'<{channel_url}>; rel="hub", <{topic_base_self_url}/{topic}>; rel="self"'
    }

    # no delivery job in delivery outbox, use case must do nothing
    delivery_outbox_repo.reset_mock()
    post.reset_mock()
    delivery_outbox_repo.get_job.return_value = None
    use_case.execute()
    post.assert_not_called()

    # delivery outbox contains a job, use case must send payload to a specified callback
    # with correct link headers, callback responds correctly
    delivery_outbox_repo.reset_mock()
    post.reset_mock()
    delivery_outbox_repo.get_job.return_value = queue_message_id, message
    response.status_code = HTTPStatus.OK
    use_case.execute()
    post.assert_called_once_with(callback, json=payload, headers=headers)
    delivery_outbox_repo.delete.assert_called_once_with(queue_message_id)

    # unexpected status code from callback, must resend job to delivery outbox to retry
    delivery_outbox_repo.reset_mock()
    post.reset_mock()
    delivery_outbox_repo.get_job.return_value = queue_message_id, message
    response.status_code = HTTPStatus.NOT_FOUND
    use_case.execute()
    post.assert_called_once_with(callback, json=payload, headers=headers)
    delivery_outbox_repo.post_job({**message, 'retry': 2})
    delivery_outbox_repo.delete.assert_called_once_with(queue_message_id)

    # can not connect to callback server, must resend job to delivery outbox to retry
    delivery_outbox_repo.reset_mock()
    post.reset_mock()
    delivery_outbox_repo.get_job.return_value = queue_message_id, message
    response.status_code = HTTPStatus.OK
    post.side_effect = requests.exceptions.RequestException()
    use_case.execute()
    post.assert_called_once_with(callback, json=payload, headers=headers)
    delivery_outbox_repo.post_job({**message, 'retry': 2})
    delivery_outbox_repo.delete.assert_called_once_with(queue_message_id)

    # another callback failure, but MAX_ATTEMPTS reached, must stop retry attempts
    delivery_outbox_repo.reset_mock()
    post.reset_mock()
    delivery_outbox_repo.get_job.return_value = queue_message_id, {**message, 'retry': use_case.MAX_ATTEMPTS}
    response.status_code = HTTPStatus.NOT_FOUND
    use_case.execute()
    post.assert_called_once_with(callback, json=payload, headers=headers)
    delivery_outbox_repo.post_job.assert_not_called()
    delivery_outbox_repo.delete.assert_called_once_with(queue_message_id)
