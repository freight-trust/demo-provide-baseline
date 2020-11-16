from http import HTTPStatus
from unittest import mock
from collections import OrderedDict
import urllib
import requests
import pytest
from src import constants
from src.api import use_cases


def test_SendMessageUseCase():
    pk = "private_key"
    contract = mock.MagicMock()
    web3 = mock.MagicMock()
    sender = 'AU'
    use_case = use_cases.SendMessageUseCase(
        web3=web3,
        contract=contract,
        contract_owner_private_key=pk
    )
    message = {
        'subject': 'subject',
        'predicate': 'predicate',
        'obj': 'object',
        'receiver': 'GB'
    }
    complete_message = {
        **message,
        'sender': sender
    }

    # invalid message structure
    with pytest.raises(use_cases.BadParametersError):
        use_case.execute({'message': {'text': 'Hello world!'}}, sender)
    contract.functions.send.assert_not_called()

    with pytest.raises(use_cases.BadParametersError):
        use_case.execute({**message, 'sender': 'GB'}, sender)
    contract.functions.send.assert_not_called()

    # valid message structure
    web3.eth.sendRawTransaction().hex.return_value = 'transaction_hash'
    result = use_case.execute(message, sender)

    # checking general flow of the operation, call method, sign transaction, send transaction
    contract.functions.send.assert_called_once_with(complete_message)
    contract.functions.send().buildTransaction.assert_called_once()
    tx = contract.functions.send().buildTransaction()
    web3.eth.account.sign_transaction.assert_called_once_with(tx, private_key=pk)
    signed_tx = web3.eth.account.sign_transaction()
    web3.eth.sendRawTransaction.assert_called_with(signed_tx.rawTransaction)

    assert result == {
        'id': 'transaction_hash',
        'status': constants.MessageStatus.RECEIVED,
        'message': complete_message
    }


def test_GetMessageUseCase():
    contract = mock.MagicMock()
    web3 = mock.MagicMock()
    confirmation_threshold = 3
    id = 'message_transaction_hash'
    use_case = use_cases.GetMessageUseCase(
        web3=web3,
        contract=contract,
        confirmation_threshold=confirmation_threshold
    )

    message = OrderedDict()
    message['subject'] = 'subject'
    message['predicate'] = 'predicate'
    message['obj'] = 'object'
    message['sender'] = 'AU'
    message['receiver'] = 'GB'

    send_message_input = [None, {'message': list(message.values())}]
    message = dict(message)

    # transaction doesn't exist
    web3.eth.getTransaction.side_effect = use_cases.TransactionNotFound()
    with pytest.raises(use_cases.NotFoundError):
        use_case.execute(id=id)
    web3.eth.getTransaction.assert_called_once_with(id)

    # resetting & configuring mocks
    web3.reset_mock()
    web3.eth.blockNumber = confirmation_threshold * 10
    web3.eth.getTransaction.side_effect = None
    contract.decode_function_input.return_value = send_message_input
    tx_receipt = mock.MagicMock()
    web3.eth.getTransactionReceipt.return_value = tx_receipt

    # message status undeliverable, unable to mine block
    tx_receipt.status = False
    result = use_case.execute(id=id)
    assert result == {
        'id': id,
        'status': constants.MessageStatus.UNDELIVERABLE,
        'message': message
    }

    # message status received, block is not yet added to blockchain
    tx_receipt.status = True
    tx_receipt.blockNumber = None
    result = use_case.execute(id=id)
    assert result == {
        'id': id,
        'status': constants.MessageStatus.RECEIVED,
        'message': message
    }

    # message status confirmed, the block has several blocks ahead
    tx_receipt.status = True
    tx_receipt.blockNumber = web3.eth.blockNumber - confirmation_threshold - 1
    result = use_case.execute(id=id)
    assert result == {
        'id': id,
        'status': constants.MessageStatus.CONFIRMED,
        'message': message
    }

    # message status received, the block has not enough blocks ahead
    tx_receipt.status = True
    tx_receipt.blockNumber = web3.eth.blockNumber
    result = use_case.execute(id=id)
    assert result == {
        'id': id,
        'status': constants.MessageStatus.RECEIVED,
        'message': message
    }


def test_GetParticipantsUseCase():
    # must call contract getParticipants methods
    contract = mock.MagicMock()
    participants = ['GB', 'UA']
    use_case = use_cases.GetParticipantsUseCase(contract)
    contract.functions.getParticipants().call.return_value = participants
    assert use_case.execute() == participants
    contract.functions.getParticipants().call.assert_called_once_with()


def test_GetTopicUseCase():
    use_case = use_cases.GetTopicUseCase()
    # invalid topics must fail with NotFoundError error
    for topic in [
        'a.b.c*',
        'a/b/c'
    ]:
        with pytest.raises(use_cases.NotFoundError):
            use_case.execute(topic)
    # valid topic, use case will return it unaltered
    assert use_case.execute('a.b.c') == 'a.b.c'


@mock.patch('src.api.use_cases.requests')
def test_CanonicalURLTopicVerificationUseCase(requests):
    topic_base_url = 'http://channel.topic/topic/'
    use_case = use_cases.CanonicalURLTopicVerificationUseCase(topic_base_url=topic_base_url)

    # testing simple string topic, not url
    topic = 'a.b.c'
    topic_prefix = 'jurisdiction'
    verified_topic = 'jurisdiction.a.b.c'

    assert use_case.execute(topic=topic, topic_prefix=topic_prefix) == verified_topic
    requests.get.assert_not_called()

    # invalid simple string topic
    topic = 'a.b.c*'
    topic_prefix = 'jurisdiction'
    with pytest.raises(use_cases.BadParametersError):
        use_case.execute(topic=topic, topic_prefix=topic_prefix)

    # valid canonical url topic
    topic = urllib.parse.urljoin(topic_base_url, 'a.b.c')
    topic_prefix = 'jurisdiction'
    verified_topic = 'jurisdiction.a.b.c'
    prefixed_topic_url = urllib.parse.urljoin(topic_base_url, verified_topic)

    response = mock.MagicMock()
    response.json.return_value = verified_topic
    response.status_code = HTTPStatus.OK
    requests.get.return_value = response

    assert use_case.execute(topic=topic, topic_prefix=topic_prefix) == verified_topic
    requests.get.assert_called_once_with(prefixed_topic_url)

    # invalid canonical url topic
    requests.reset_mock()
    topic = urllib.parse.urljoin(topic_base_url, 'a.b.c*')
    topic_prefix = 'jurisdiction'

    with pytest.raises(use_cases.BadParametersError):
        use_case.execute(topic=topic, topic_prefix=topic_prefix)
    requests.get.assert_not_called()

    # topic url returns unexpected topic string
    requests.reset_mock()
    topic = urllib.parse.urljoin(topic_base_url, 'a.b.c')
    topic_prefix = 'jurisdiction'
    verified_topic = 'jurisdiction.a.b.c'
    prefixed_topic_url = urllib.parse.urljoin(topic_base_url, verified_topic)

    response = mock.MagicMock()
    response.json.return_value = 'unexpected.topic'
    response.status_code = HTTPStatus.OK
    requests.get.return_value = response

    with pytest.raises(use_cases.ConflictError):
        use_case.execute(topic=topic, topic_prefix=topic_prefix)
    requests.get.assert_called_once_with(prefixed_topic_url)

    # topic url returns NOT_FOUND
    requests.reset_mock()
    topic = urllib.parse.urljoin(topic_base_url, 'a.b.c')
    topic_prefix = 'jurisdiction'
    verified_topic = 'jurisdiction.a.b.c'
    prefixed_topic_url = urllib.parse.urljoin(topic_base_url, verified_topic)

    response = mock.MagicMock()
    response.status_code = HTTPStatus.NOT_FOUND
    requests.get.return_value = response

    with pytest.raises(use_cases.NotFoundError):
        use_case.execute(topic=topic, topic_prefix=topic_prefix)
    requests.get.assert_called_once_with(prefixed_topic_url)

    # topic url returns NOT_FOUND
    requests.reset_mock()
    topic = urllib.parse.urljoin(topic_base_url, 'a.b.c')
    topic_prefix = 'jurisdiction'
    verified_topic = 'jurisdiction.a.b.c'
    prefixed_topic_url = urllib.parse.urljoin(topic_base_url, verified_topic)

    response = mock.MagicMock()
    response.status_code = HTTPStatus.NOT_FOUND
    requests.get.return_value = response

    with pytest.raises(use_cases.NotFoundError):
        use_case.execute(topic=topic, topic_prefix=topic_prefix)
    requests.get.assert_called_once_with(prefixed_topic_url)

    # topic url returns unexpected response code
    requests.reset_mock()
    topic = urllib.parse.urljoin(topic_base_url, 'a.b.c')
    topic_prefix = 'jurisdiction'
    verified_topic = 'jurisdiction.a.b.c'
    prefixed_topic_url = urllib.parse.urljoin(topic_base_url, verified_topic)

    response = mock.MagicMock()
    response.status_code = HTTPStatus.BAD_REQUEST
    requests.get.return_value = response

    with pytest.raises(use_cases.UnexpectedTopicURLResponseError):
        use_case.execute(topic=topic, topic_prefix=topic_prefix)
    requests.get.assert_called_once_with(prefixed_topic_url)


@mock.patch('src.api.use_cases.requests.get')
@mock.patch('src.api.use_cases.uuid')
def test_SubscriptionCallbackVerificationUseCase(uuid, get):
    use_case = use_cases.SubscriptionCallbackVerificationUseCase()

    callback = 'callback.example/callback'
    mode = 'subscribe'
    topic = 'a.b.c'
    lease_seconds = 3600
    challenge = 'xxxx-xxx-xx'

    params = {
        'hub.mode': mode,
        'hub.topic': topic,
        'hub.lease_seconds': lease_seconds,
        'hub.challenge': challenge
    }

    uuid.uuid4.return_value = challenge

    response = mock.MagicMock()
    get.return_value = response

    # valid response will pass without an exception
    response.status_code = HTTPStatus.OK
    response.text = challenge

    get.reset_mock()
    use_case.execute(
        callback=callback,
        mode=mode,
        topic=topic,
        lease_seconds=lease_seconds
    )
    get.assert_called_once_with(callback, params)

    # invalid callback response code
    get.reset_mock()
    response.status_code = HTTPStatus.NOT_FOUND
    with pytest.raises(use_cases.CallbackURLValidationError):
        use_case.execute(
            callback=callback,
            mode=mode,
            topic=topic,
            lease_seconds=lease_seconds
        )
    get.assert_called_once_with(callback, params)

    # invalid callback challenge response
    get.reset_mock()
    response.status_code = HTTPStatus.OK
    response.text = 'invalid_challenge'
    with pytest.raises(use_cases.CallbackURLValidationError):
        use_case.execute(
            callback=callback,
            mode=mode,
            topic=topic,
            lease_seconds=lease_seconds
        )
    get.assert_called_once_with(callback, params)

    # unexpected response exception
    get.reset_mock()
    response.status_code = HTTPStatus.OK
    response.text = challenge
    get.side_effect = requests.exceptions.RequestException()
    with pytest.raises(use_cases.CallbackURLValidationError):
        use_case.execute(
            callback=callback,
            mode=mode,
            topic=topic,
            lease_seconds=lease_seconds
        )
    get.assert_called_once_with(callback, params)
