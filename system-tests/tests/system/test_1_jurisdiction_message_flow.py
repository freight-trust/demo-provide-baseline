from http import HTTPStatus


def test(
    channel_api_b,
    channel_api_a,
    callback_server
):

    """
    Testing channels participants lists.
    They must have each other on the participants list in order to communicate.
    """

    r = channel_api_a.get_participants()
    assert r.status_code == HTTPStatus.OK
    assert r.json() == [channel_api_b.sender]
    r = channel_api_b.get_participants()
    assert r.status_code == HTTPStatus.OK
    assert r.json() == [channel_api_a.sender]

    """
    Posting subscriptions to "jurisdiction.<channel_api_a.sender>" and "jurisdiction.<channel_api_b.sender>" topics.
    Currenly the only topics that cause notifications are "jurisdiction.<RECEIVER>" topics.
    All the subscriptions below are equivalent. The difference there is the way the topic
    is initially presented: unprefixed, prefixed, canonical url.
    """
    # PREFIXED TOPICS

    r = channel_api_a.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('prefixed.jurisdiction.channel.a'),
        'hub.topic': channel_api_a.sender,
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    r = channel_api_b.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('prefixed.jurisdiction.channel.b'),
        'hub.topic': channel_api_b.sender,
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    # PREFIXED CANONICAL URL TOPICS
    r = channel_api_a.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('url.jurisdiction.channel.a'),
        'hub.topic': channel_api_a.get_topic_url(channel_api_a.sender),
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    r = channel_api_b.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('url.jurisdiction.channel.b'),
        'hub.topic': channel_api_b.get_topic_url(channel_api_b.sender),
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    # UNPREFIXED TOPICS
    r = channel_api_a.post_subscription_by_id({
        'hub.callback': callback_server.valid_callback_url('unprefixed.jurisdiction.channel.a'),
        'hub.topic': 'jurisdiction.' + channel_api_a.sender,
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    r = channel_api_b.post_subscription_by_id({
        'hub.callback': callback_server.valid_callback_url('unprefixed.jurisdiction.channel.b'),
        'hub.topic': 'jurisdiction.' + channel_api_b.sender,
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    # UNPREFIXED TOPICS that should not receive notifications
    r = channel_api_b.post_subscription_by_id({
        'hub.callback': callback_server.valid_callback_url('not.notify.channel.a'),
        'hub.topic': channel_api_a.sender,
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    r = channel_api_b.post_subscription_by_id({
        'hub.callback': callback_server.valid_callback_url('not.notify.channel.b'),
        'hub.topic': channel_api_b.sender,
        'hub.lease_seconds': 3600,
        'hub.mode': 'subscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    # shortcuts for the callback received message verifications
    def verify_callback_message_received(message, callback_id):
        records = callback_server.get_callback_records(
            id=callback_id,
            attemps=3,
            delay=1,
            interval=5
        )

        assert len(records) == 1
        assert records[0]['json'] == {'id': message['id']}

    def verify_callback_not_received_message(callback_id):
        assert not callback_server.get_callback_records(
            id=callback_id,
            attemps=3,
            delay=1,
            interval=5
        )

    def post_message(channel_api, message_data):
        r = channel_api.post_message(message_data)
        assert r.status_code == HTTPStatus.OK
        message = r.json()
        assert 'id' in message
        assert 'message' in message
        assert message['message'] == {
            **message_data,
            'sender': channel_api.sender
        }
        # testing that message added to a blockchain
        r = channel_api.get_message(message['id'])
        # testing that message recorded as expected
        assert r.status_code == HTTPStatus.OK
        assert r.json() == message, r.text
        return message

    """
    Posting the message from channel_api_a to channel_api_b
    Receivers(callback ids):
        1. prefixed.jurisdiction.channel.b
        2. url.jurisdiction.channel.b
        3. unprefixed.jurisdiction.channel.b
    Ignored by(callback ids):
        1. not.notify.channel.b
        2. not.notify.channel.a
        3. prefixed.jurisdiction.channel.a
        4. url.jurisdiction.channel.a
        5. unprefixed.jurisdiction.channel.a
    """

    # clearing callback server records to remove records of the previous callbacks
    callback_server.clear_callback_records()

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "obj": "hello world",
        "receiver": channel_api_b.sender
    }

    message = post_message(channel_api_a, message)

    # verify expected receivers
    verify_callback_message_received(message, 'prefixed.jurisdiction.channel.b')
    verify_callback_message_received(message, 'url.jurisdiction.channel.b')
    verify_callback_message_received(message, 'unprefixed.jurisdiction.channel.b')
    # verify ignored receivers
    verify_callback_not_received_message('not.notify.channel.b')
    verify_callback_not_received_message('not.notify.channel.a')
    verify_callback_not_received_message('prefixed.jurisdiction.channel.a')
    verify_callback_not_received_message('url.jurisdiction.channel.a')
    verify_callback_not_received_message('unprefixed.jurisdiction.channel.a')

    """
    Posting the message from channel_api_b to channel_api_a
    Receivers(callback ids):
        1. prefixed.jurisdiction.channel.a
        2. url.jurisdiction.channel.a
        3. unprefixed.jurisdiction.channel.a
    Ignored by(callback ids):
        1. not.notify.channel.b
        2. not.notify.channel.a
        3. prefixed.jurisdiction.channel.b
        4. url.jurisdiction.channel.b
        5. unprefixed.jurisdiction.channel.b
    """

    # clearing callback server records to remove records of the previous callbacks
    callback_server.clear_callback_records()

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "obj": "hello world",
        "receiver": channel_api_a.sender
    }

    message = post_message(channel_api_b, message)

    # verify expected receivers
    verify_callback_message_received(message, 'prefixed.jurisdiction.channel.a')
    verify_callback_message_received(message, 'url.jurisdiction.channel.a')
    verify_callback_message_received(message, 'unprefixed.jurisdiction.channel.a')
    # verify ignored receivers
    verify_callback_not_received_message('not.notify.channel.b')
    verify_callback_not_received_message('not.notify.channel.a')
    verify_callback_not_received_message('prefixed.jurisdiction.channel.b')
    verify_callback_not_received_message('url.jurisdiction.channel.b')
    verify_callback_not_received_message('unprefixed.jurisdiction.channel.b')

    """
    Testing that deleted subscriptions will not receive notifications.
    There are 3 variants of subscription. Each supports unsubscribe mode.
    Unsubscribing one by one and testing that after all they will not receive any messages.
    """

    # clearing callback server records to remove records of the previous callbacks
    callback_server.clear_callback_records()

    # UNSUBSCRIBE FROM PREFIXED TOPIC
    r = channel_api_a.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('prefixed.jurisdiction.channel.a'),
        'hub.topic': channel_api_a.sender,
        'hub.lease_seconds': 3600,
        'hub.mode': 'unsubscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "obj": "hello world",
        "receiver": channel_api_a.sender
    }

    message = post_message(channel_api_b, message)
    # verify expected receivers
    verify_callback_message_received(message, 'url.jurisdiction.channel.a')
    verify_callback_message_received(message, 'unprefixed.jurisdiction.channel.a')
    # verify ignored receivers
    verify_callback_not_received_message('prefixed.jurisdiction.channel.a')

    # clearing callback server records to remove records of the previous callbacks
    callback_server.clear_callback_records()

    # UNSUBSCRIBE FROM UNPREFIXED TOPIC
    r = channel_api_a.post_subscription_by_id({
        'hub.callback': callback_server.valid_callback_url('unprefixed.jurisdiction.channel.a'),
        'hub.topic': 'jurisdiction.' + channel_api_a.sender,
        'hub.lease_seconds': 3600,
        'hub.mode': 'unsubscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "obj": "hello world",
        "receiver": channel_api_a.sender
    }

    message = post_message(channel_api_b, message)
    # verify expected receivers
    verify_callback_message_received(message, 'url.jurisdiction.channel.a')
    # verify ignored receivers
    verify_callback_not_received_message('unprefixed.jurisdiction.channel.a')
    verify_callback_not_received_message('prefixed.jurisdiction.channel.a')

    # clearing callback server records to remove records of the previous callbacks
    callback_server.clear_callback_records()

    # UNSUBSCRIBE FROM PREFIXED CANONICAL URL TOPIC
    r = channel_api_a.post_subscription_by_jurisdiction({
        'hub.callback': callback_server.valid_callback_url('url.jurisdiction.channel.a'),
        'hub.topic': channel_api_a.get_topic_url(channel_api_a.sender),
        'hub.lease_seconds': 3600,
        'hub.mode': 'unsubscribe'
    })
    assert r.status_code == HTTPStatus.OK, r.text

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "obj": "hello world",
        "receiver": channel_api_a.sender
    }

    message = post_message(channel_api_b, message)
    # verify ignored receivers
    verify_callback_not_received_message('url.jurisdiction.channel.a')
    verify_callback_not_received_message('unprefixed.jurisdiction.channel.a')
    verify_callback_not_received_message('prefixed.jurisdiction.channel.a')
