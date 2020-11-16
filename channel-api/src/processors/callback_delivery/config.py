from box import Box
from libtrustbridge.utils.conf import env_queue_config, env


def Config():
    environment_config = dict(
        DELIVERY_OUTBOX_REPO=env_queue_config('DELIVERY_OUTBOX_REPO'),
        TOPIC_BASE_SELF_URL=env('TOPIC_BASE_SELF_URL', '/topic'),
        CHANNEL_URL=env('CHANNEL_URL')
    )
    return Box(environment_config)
