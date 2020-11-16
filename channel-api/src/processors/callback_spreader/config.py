from box import Box
from libtrustbridge.utils.conf import env_queue_config, env_s3_config


def Config():
    environment_config = dict(
        NOTIFICATIONS_REPO=env_queue_config('NOTIFICATIONS_REPO'),
        DELIVERY_OUTBOX_REPO=env_queue_config('DELIVERY_OUTBOX_REPO'),
        SUBSCRIPTIONS_REPO=env_s3_config('SUBSCRIPTIONS_REPO')
    )
    return Box(environment_config)
