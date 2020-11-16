from box import Box
from libtrustbridge.websub.repos import (
    SubscriptionsRepo,
    NotificationsRepo,
    DeliveryOutboxRepo
)
from libtrustbridge.repos.elasticmqrepo import ElasticMQRepo
from libtrustbridge.repos.miniorepo import MinioRepo


class Channel(ElasticMQRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)


class Contract(MinioRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)


class Subscriptions(SubscriptionsRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)


class Notifications(NotificationsRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)


class DeliveryOutbox(DeliveryOutboxRepo):
    def __init__(self, config: Box = None):
        super().__init__(config)
