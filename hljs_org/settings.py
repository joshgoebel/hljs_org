import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hljs_org',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'hljs_org.urls'
WSGI_APPLICATION = 'hljs_org.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hljs_org',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = False
USE_L10N = False
USE_TZ = True

STATIC_URL = '/static/'

TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'hljs_org', 'templates'),
]

SECRET_KEY = 'l4=eul9(8$7-mo-xq=%4_z=r4mefs33izqmc8&_&lis#1v6b7&'

## Custom settings

HLJS_SOURCE = '/home/maniac/code/hljs/highlight.js'
HLJS_CACHE = '/home/maniac/code/hljs/cache'

sys.path.insert(0, os.path.join(HLJS_SOURCE, 'tools'))

import logging
logger = logging.getLogger('hljs_org')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
