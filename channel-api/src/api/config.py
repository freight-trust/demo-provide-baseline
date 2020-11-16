from box import Box
from libtrustbridge.utils.conf import env_s3_config, env, env_bool


def Config():
    environment_config = dict(
        SUBSCRIPTIONS_REPO=env_s3_config('SUBSCRIPTIONS_REPO'),
        # api base url, ex: https://test.api.com
        CHANNEL_URL=env('CHANNEL_URL'),

        TESTING=env_bool('TESTING', default=False),
        DEBUG=env_bool('DEBUG', default=False),

        HTTP_BLOCKCHAIN_ENDPOINT=env('HTTP_BLOCKCHAIN_ENDPOINT'),

        CONTRACT_REPO=env_s3_config('CONTRACT_REPO'),
        CONTRACT_BUILD_ARTIFACT_KEY=env('CONTRACT_BUILD_ARTIFACT_KEY'),
        CONTRACT_NETWORK_ID=str(int(env('CONTRACT_NETWORK_ID', default=1))),
        CONTRACT_OWNER_PRIVATE_KEY=env('CONTRACT_OWNER_PRIVATE_KEY'),

        MESSAGE_CONFIRMATION_THRESHOLD=int(env('CONFIRMATION_THRESHOLD', default='12')),

        SENDER=env('SENDER', default='AU')
    )
    return Box(environment_config)
