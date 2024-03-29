from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')  # noqa

RAVEN_CONFIG = {
    'dsn': os.environ.get('DSN_URL'),  # noqa
}

INSTALLED_APPS = INSTALLED_APPS + [  # noqa
    'raven.contrib.django.raven_compat',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'apps.afiliacion.api.views': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
        },
        'apps.servicios.api.views': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
        },
        'apps.afiliacion.forms': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING',
        },
    },
}
