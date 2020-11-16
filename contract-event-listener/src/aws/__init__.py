import os
import boto3


DEFAULT_CONFIG = {
    'endpoint_url': os.environ.get('AWS_ENDPOINT_URL')
}


def __full_config(config):
    config = config or {}
    return {**DEFAULT_CONFIG, **config}


def s3(config=None):
    return boto3.resource('s3', **__full_config(config))


def sqs(config=None):
    return boto3.resource('sqs', **__full_config(config))
