import urllib
from box import Box
from flask import Flask
from web3 import Web3
from libtrustbridge.errors import handlers as error_handlers
from src import repos
from . import views as api
from .contract import Contract


def create_app(config: Box = None):
    app = Flask(__name__)
    app.config = Box(app.config)
    app.config.update(config)
    with app.app_context():

        app.web3 = Web3(Web3.HTTPProvider(config.HTTP_BLOCKCHAIN_ENDPOINT))
        app.repos = Box(
            subscriptions=repos.Subscriptions(config=config.SUBSCRIPTIONS_REPO),
            contract=repos.Contract(config=config.CONTRACT_REPO)
        )
        app.contract = Contract(
            web3=app.web3,
            repo=app.repos.contract,
            network_id=config.CONTRACT_NETWORK_ID,
            artifact_key=config.CONTRACT_BUILD_ARTIFACT_KEY
        )

        app.register_blueprint(api.blueprint)
        error_handlers.register(app)

        app.config.TOPIC_BASE_URL = urllib.parse.urljoin(config.CHANNEL_URL, api.TOPIC_BASE_URL)

    return app
