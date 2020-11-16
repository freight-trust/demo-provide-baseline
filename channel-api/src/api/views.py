from http import HTTPStatus
from libtrustbridge.utils.routing import mimetype
from flask import Blueprint, request, current_app as app, jsonify
from . import utils
from .use_cases import (
    GetParticipantsUseCase,
    GetMessageUseCase,
    SendMessageUseCase,
    GetTopicUseCase,
    SubscriptionActionUseCase
)


blueprint = Blueprint('api', __name__)


@blueprint.route('/messages', methods=['POST'])
@mimetype(include=['application/json'])
def post_messages():
    result = SendMessageUseCase(
        app.web3,
        app.contract,
        app.config.CONTRACT_OWNER_PRIVATE_KEY
    ).execute(
        request.json,
        app.config.SENDER
    )
    return jsonify(result)


@blueprint.route('/messages/<id>', methods=['GET'])
def get_messages(id):
    return jsonify(GetMessageUseCase(app.web3, app.contract, app.config.MESSAGE_CONFIRMATION_THRESHOLD).execute(id))


@blueprint.route('/participants', methods=['GET'])
def get_participants():
    return jsonify(GetParticipantsUseCase(app.contract).execute())


TOPIC_BASE_URL = 'topic'


@blueprint.route(f'/{TOPIC_BASE_URL}/<topic>', methods=['GET'])
def get_topic(topic):
    return jsonify(GetTopicUseCase().execute(topic))


@blueprint.route('/messages/subscriptions/by_id', methods=['POST'])
@blueprint.route('/messages/subscriptions/by_jurisdiction', methods=['POST'])
@mimetype(include=['application/x-www-form-urlencoded'])
@utils.form
def subscriptions(form_data):
    topic_prefix = ''
    if request.url.endswith('by_jurisdiction'):
        topic_prefix = 'jurisdiction'
    SubscriptionActionUseCase(
        subscriptions_repo=app.repos.subscriptions,
        topic_base_url=app.config.TOPIC_BASE_URL
    ).execute(form_data, topic_prefix)
    return ('', HTTPStatus.OK)
