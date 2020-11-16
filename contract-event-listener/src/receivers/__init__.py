import json
from src import aws
from src import config
from src.loggers import logging
from src.utils.jmespath_json_template import JMESPathJSONTemplate


class Receiver:
    @staticmethod
    def from_config(config_obj):
        if config_obj.Type == config.Receiver.Type.SQS:
            return SQSReceiver(config_obj)
        elif config_obj.Type == config.Receiver.Type.LOG:
            return LogReceiver(config_obj)

    @staticmethod
    def mapping_from_list(receiver_list):
        mapping = dict()
        for config_obj in receiver_list:
            mapping[config_obj.Id] = Receiver.from_config(config_obj)
        return mapping

    def __init__(self, config):
        self.config = config
        self.jmespath_json_template = JMESPathJSONTemplate(self.config.JSON) if self.config.JSON else None

    def process_message_data(self, message):
        if self.jmespath_json_template:
            message = self.jmespath_json_template.render(message)
        return message

    def send(self, message):
        self.send_message(self.process_message_data(message))


class SQSReceiver(Receiver):
    def __init__(self, config_obj):
        super().__init__(config_obj)
        self.__logger = logging.getLogger(self.config.Id)
        self.__queue = aws.sqs(config_obj.Config.AWS).Queue(config_obj.QueueUrl)

    def send_message(self, message):
        kwargs = {**self.config.Config.Message, 'MessageBody': json.dumps(message)}
        self.__logger.debug('Sending the message to %s', self.config.QueueUrl)
        self.__logger.debug(message)
        self.__queue.send_message(**kwargs)
        self.__logger.debug('Message sent')


class LogReceiver(Receiver):
    def __init__(self, config_obj):
        super().__init__(config_obj)
        self.__logger = logging.getLogger(self.config.Id)

    def send_message(self, message):
        self.__logger.info(message)
