from .base import *  # noqa

ALLOWED_HOSTS = ['*', ]

DEBUG = True

INSTALLED_APPS += [  # noqa
    'debug_toolbar',
    'django_extensions'
]

MIDDLEWARE += [  # noqa
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = 'dev.minsa.gob.pe'
