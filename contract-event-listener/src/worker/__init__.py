import os
import time
from web3 import Web3
from src.contract import Contract
from src.receivers import Receiver
from src.listener import Listener
from src.loggers import logging


class Worker:

    def __init__(self, config):
        self.config = config
        os.makedirs(config.Worker.General.ListenerBlocksLogDir, exist_ok=True)
        web3 = Web3(Web3.WebsocketProvider(config.Worker.Blockchain.URI))
        contract = Contract(web3, config.Worker.Contract)
        receivers = Receiver.mapping_from_list(config.Receivers)
        self.listeners = Listener.from_config_list(
            contract,
            receivers,
            config.Listeners,
            config
        )
        self.logger = logging.getLogger(config.Worker.General.LoggerName)

    def poll(self):
        for listener in self.listeners:
            listener.poll()

    def run(self):  # pragma: no cover
        try:
            while True:
                self.poll()
                time.sleep(self.config.Worker.General.PollingInterval)
        except KeyboardInterrupt:
            pass
