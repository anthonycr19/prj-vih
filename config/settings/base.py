import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AUTH_USER_MODEL = 'cauth.User'

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True

LANGUAGE_CODE = 'es-PE'

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_L10N = False

USE_TZ = True

MEDIA_URL = os.environ.get('MEDIA', '/media/')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = os.environ.get('STATIC_URL', '/static/')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'apps', 'static'),
)

DJANGO_ADMIN_APPS = [
    'flat',
]
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'crispy_forms',
    'minsalogin',
    'simple_history',
    'rest_framework',
    'django_filters',
    'rest_framework_docs',
]
LOCAL_APPS = [
    'apps.cauth',
    'apps.common',
    'apps.afiliacion',
    'apps.medicamentos',
    'apps.dashboard',
    'apps.laboratorio',
    'apps.atencion',
    'apps.antecedente',
    'apps.consejeria',
]
INSTALLED_APPS = DJANGO_ADMIN_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

LOGIN_URL = '/accounts/login/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
    }
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# jasper reports
JASPER_URL = os.environ.get('JASPER_URL')
JASPER_USER = os.environ.get('JASPER_USER')
JASPER_PASSWORD = os.environ.get('JASPER_PASSWORD')
JASPER_PATH = os.environ.get('JASPER_PATH')

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_DOMAIN = os.environ.get('LOGIN_DOMAIN')
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# LOGIN
APP_IDENTIFIER = os.environ.get('APP_IDENTIFIER')
CURRENT_DOMAIN = os.environ.get('CURRENT_DOMAIN')
URL_LOGIN_SERVER = os.environ.get('LOGIN_HOST_URL')

# MPI
API_VERSION = 'v1'
MPI_API_HOST = os.environ.get('MPI_API_HOST')
MPI_API_TOKEN = os.environ.get('MPI_API_TOKEN')
API_MPI_URL = '{}/api/{}'.format(MPI_API_HOST, API_VERSION)

# CITAS
CITAS_API_HOST = os.environ.get('CITAS_API_HOST')
CITAS_API_TOKEN = os.environ.get('CITAS_API_TOKEN')
API_CITA_URL = '{}/api'.format(CITAS_API_HOST)

# INMUNIZACIONES
URL_INMUNIZACIONES_SERVER = os.environ.get('INMUNIZACIONES_HOST_URL')

REST_FRAMEWORK = {
    'SEARCH_PARAM': 'q',
    'PAGE_SIZE': 25,
    'DATE_INPUT_FORMATS': ('iso-8601', '%d/%m/%Y', '%Y-%m-%d'),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend', ),
    'EXCEPTION_HANDLER': 'rest_framework_json_api.exceptions.exception_handler',
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework_json_api.pagination.PageNumberPagination',
}

# CATALOGO ODOO
CATALOGO_ODOO_TOKEN = os.environ.get('CATALOGO_ODOO_TOKEN')
CATALOGO_ODOO_HOST_URL = os.environ.get('CATALOGO_ODOO_HOST_URL')

# UPS APLICADAS VIH
UPS_LABORATORIO = os.environ.get('UPS_LABORATORIO')
UPS_EGRESO = os.environ.get('UPS_EGRESO')
