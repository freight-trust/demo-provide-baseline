import os
import json
from web3 import Web3
from src.loggers import logging


class Listener:

    @staticmethod
    def from_config_list(contract=None, receivers=None, config_list=None, global_config=None):
        return [Listener(contract, receivers, config, global_config) for config in config_list]

    def __load_from_block(self):
        try:
            with open(self.__from_block_filename, 'rt') as f:
                value = int(f.read())
                self.__logger.debug('from block=%s file loaded', value)
                return value
        except (ValueError, FileNotFoundError):
            return 0

    def __update_from_block(self, value):
        with open(self.__from_block_filename, 'wt+') as f:
            f.write(str(value))
        self.__logger.debug('from block updated=%s', value)

    def __update_filter(self):
        config = self.__config
        contract = self.__contract
        from_block = self.__from_block
        default_filter_config = {'fromBlock': from_block, 'toBlock': 'latest'}
        filter_config = {**default_filter_config, **config.Event.Filter}
        # if we are replacing previous filter
        if self.__filter is not None:
            filter_config['fromBlock'] = self.__from_block
        self.__filter = contract.events[config.Event.Name].createFilter(**filter_config)
        self.__logger.debug('new filter=%s', filter_config)

    def __init__(self, contract=None, receivers=None, config=None, global_config=None):
        self.__logger = logging.getLogger(config.Id)

        self.__contract = contract
        self.__config = config
        self.__global_config = global_config
        self.__receivers = tuple(receivers[id] for id in config.Receivers)
        self.__from_block_filename = os.path.join(global_config.Worker.General.ListenerBlocksLogDir, config.Id)
        self.__from_block = self.__load_from_block()
        self.__filter = None
        self.__update_filter()

    def poll(self):
        new_from_block = self.__from_block
        event_received = False
        event_count = 0
        for event in self.__filter.get_all_entries():
            self.__logger.debug('event received')
            self.__logger.debug('event.blockNumber=%s', event.blockNumber)
            # update filter if initial "fromBlock" = "latest"
            event_received = True
            # DUPLICATES AVOIDANCE
            if event.blockNumber < new_from_block:
                self.__logger.debug('event was already seen, ignored.')
                continue
            # start new filter from the next block
            new_from_block = event.blockNumber + 1
            message = json.loads(Web3.toJSON(event))
            event_count += 1
            for receiver in self.__receivers:
                receiver.send(message)
        if event_received:
            self.__logger.debug('events count=%s', event_count)
            self.__from_block = new_from_block
            self.__update_from_block(new_from_block)
            self.__update_filter()
