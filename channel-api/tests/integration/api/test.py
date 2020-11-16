"""
This test relies on the correct environment setup.
Setup must contain two deployed contracts that are interlinked as participants.
The sender(used in the test) contract is 'AU',
and the receiver(required by the sender to send messages) contract is 'GB'.
"""
import uuid
from http import HTTPStatus
import pytest
from libtrustbridge.websub.domain import Pattern


def test_post_get_message(client, app):
    # testing message with sender property set

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "obj": "object",
        "receiver": "GB",
        "sender": "AU"
    }

    response = client.post('/messages', json=message)
    assert response.status_code == HTTPStatus.OK
    assert 'id' in response.json
    assert response.json['id']
    assert isinstance(response.json['id'], str)
    assert 'status' in response.json
    assert response.json['status'] == 'received'
    message = {
        **message,
        'sender': app.config.SENDER
    }
    assert response.json['message'] == message
    message_id = response.json['id']

    # testing message without sender property, should be added automatically

    message = {
        "subject": "subject",
        "predicate": "predicate",
        "obj": "object",
        "receiver": "GB"
    }

    response = client.post('/messages', json=message)
    assert response.status_code == HTTPStatus.OK
    assert 'id' in response.json
    assert response.json['id']
    assert isinstance(response.json['id'], str)
    assert 'status' in response.json
    assert response.json['status'] == 'received'
    message = {
        **message,
        'sender': app.config.SENDER
    }
    assert response.json['message'] == message
    message_id = response.json['id']

    # testing that message added to the blockchain
    response = client.get(f'/messages/{message_id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        'id': message_id,
        'message': message,
        'status': 'received'
    }

    # testing that non existing message returns 404
    message_id = uuid.uuid4().hex
    response = client.get(f'/messages/{message_id}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json['errors'][0]['detail'] == f'Message {{id:"{message_id}"}} not found'


def test_get_participants(client):
    response = client.get('/participants')
    assert response.status_code == HTTPStatus.OK
    assert response.json == ['GB']


def test_get_topic(client):
    topics = [
        'a',
        'a.b'
        'a.b.c',
        'a.b.c.*'
    ]
    for topic in topics:
        response = client.get(f'/topic/{topic}')
        assert response.status_code == HTTPStatus.OK
        assert response.json == topic
    invalid_topics = [
        'a/b/c',
        'a.b.c*'
        ''
    ]
    for invalid_topic in invalid_topics:
        response = client.get(f'/topic/{invalid_topic}')
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url,topic,pattern',
    [
        ['/messages/subscriptions/by_id', 'a.b.c', 'a.b.c'],
        ['/messages/subscriptions/by_id', '{TOPIC_BASE_URL}a.b.c', 'a.b.c'],
        ['/messages/subscriptions/by_jurisdiction', 'AU', 'jurisdiction.AU'],
        ['/messages/subscriptions/by_jurisdiction', '{TOPIC_BASE_URL}AU', 'jurisdiction.AU'],
    ]
)
def test_subscriptions(client, app, subscriptions_repo, callback_server, url, topic, pattern):
    topic = topic.format(TOPIC_BASE_URL=f'{app.config.TOPIC_BASE_URL}/')
    subscription_callback = callback_server.valid_callback_url(1)
    data = {
        'hub.mode': 'subscribe',
        'hub.topic': topic,
        'hub.lease_seconds': 3600,
        'hub.callback': subscription_callback
    }
    # creating subscription
    # checking that the subscription does not exist
    assert not subscriptions_repo.get_subscriptions_by_pattern(Pattern(pattern))
    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.OK, response.json
    # checking that a single subscription was created for the expected pattern
    assert len(subscriptions_repo.get_subscriptions_by_pattern(Pattern(pattern))) == 1
    # deleting subcription
    data['hub.mode'] = 'unsubscribe'
    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.OK, response.json
    # subscription can't be deleted if it does not exist
    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json


@pytest.mark.parametrize(
    'url',
    [
        '/messages/subscriptions/by_id',
        '/messages/subscriptions/by_jurisdiction'
    ]
)
def test_subscriptions_errors(client, app, subscriptions_repo, callback_server, url):

    topic = 'a.b.c'
    data = {
        'hub.mode': 'subscribe',
        'hub.topic': topic,
    }
    # subscription request will not pass form data verification
    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json

    topic = 'a.b.c'
    data = {
        'hub.mode': 'subscribe',
        'hub.topic': topic,
        'hub.lease_seconds': 3600,
        'hub.callback': callback_server.invalid_callback_url('invalid_callback_error')
    }
    # subscription request will not pass callback verification
    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json
    assert callback_server.get_callback_record(-1)['id'] == 'invalid_callback_error'

    topic = 'a.b.c*'
    data = {
        'hub.mode': 'subscribe',
        'hub.topic': topic,
        'hub.lease_seconds': 3600,
        'hub.callback': callback_server.valid_callback_url('valid_callback_url')
    }
    # subscription request will not pass topic verification
    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json

    # testing invalid topic url
    topic = f'{app.config.TOPIC_BASE_URL}/a.b.c*'
    data = {
        'hub.mode': 'subscribe',
        'hub.topic': topic,
        'hub.lease_seconds': 3600,
        'hub.callback': callback_server.valid_callback_url('valid_callback_url')
    }
    # subscription request will not pass topic verification
    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json

    # testing invalid topic base url
    topic = 'http://topic.localhost/topic/a.b.c*'
    data = {
        'hub.mode': 'subscribe',
        'hub.topic': topic,
        'hub.lease_seconds': 3600,
        'hub.callback': callback_server.valid_callback_url('valid_callback_url')
    }
    # subscription request will not pass topic verification
    response = client.post(url, data=data, mimetype='application/x-www-form-urlencoded')
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json
