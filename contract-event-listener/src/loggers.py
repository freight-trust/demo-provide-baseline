import os
import logging
from logging.config import dictConfig
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


SENTRY_DSN = os.environ.get('SENTRY_DSN', default=None)
SENTRY_ENVIRONMENT = os.environ.get('SENTRY_ENVIRONMENT', default=None)
SENTRY_RELEASE = os.environ.get('SENTRY_RELEASE', default=None)


if SENTRY_DSN:  # pragma: no cover
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    sentry_sdk_init_kwargs = dict(
        dsn=SENTRY_DSN,
        integrations=[sentry_logging]
    )
    if SENTRY_ENVIRONMENT:
        sentry_sdk_init_kwargs['environment'] = SENTRY_ENVIRONMENT
    if SENTRY_RELEASE:
        sentry_sdk_init_kwargs['release'] = SENTRY_RELEASE
    sentry_sdk.init(**sentry_sdk_init_kwargs)


LOGGING = {
    'version': 1,
    'disableExistingLoggers': False,
    'formatters': {
        'default': {
            'format': '[%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG' if os.environ.get('DEBUG', '').lower() in ['true', '1'] else 'INFO',
            'handlers': ['console'],
        }
    }
}


dictConfig(LOGGING)

root = logging.getLogger()
