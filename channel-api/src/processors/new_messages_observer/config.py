from box import Box
from libtrustbridge.utils.conf import env_queue_config, env


def Config():
    environment_config = dict(
        NOTIFICATIONS_REPO=env_queue_config('NOTIFICATIONS_REPO'),
        CHANNEL_REPO=env_queue_config('CHANNEL_REPO'),
        RECEIVER=env('RECEIVER')
    )
    return Box(environment_config)
