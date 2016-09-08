# coding: utf-8

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'm2mkt*3)e@sc3t)l&&q8xbgarxe&+a@=l$g1ga2wnv@ikbia+='

DEBUG = True

ALLOWED_HOSTS = []

# Celery
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
BROKER_URL = 'redis://localhost:{}/{}'.format(REDIS_PORT, REDIS_DB)
CELERY_RESULT_BACKEND = 'redis://localhost:{}/{}'.format(REDIS_PORT, REDIS_DB)
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}  # 1 hour.
CELERY_ENABLE_UTC = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

# Application definition
INSTALLED_APPS = (
    'main',
    'djcelery',

    'django_extensions',
    'rest_framework',

    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',
)

import djcelery
djcelery.setup_loader()

MIDDLEWARE_CLASSES = (
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'main.urls'

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            os.path.join(BASE_DIR, 'templates'),
        ),
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'main.context_processors.preload',
            ],
            'loaders': (
              'django.template.loaders.filesystem.Loader',
              'django.template.loaders.app_directories.Loader',
              'django.template.loaders.eggs.Loader',
            ),
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

STATIC_DIR = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

PAGE_SIZE = 3

CACHE_VERSION = 1
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '%s:%s:%s' % (REDIS_HOST, REDIS_PORT, REDIS_DB),
        'OPTIONS': {
            "PARSER_CLASS": "redis.connection.HiredisParser",
        },
        'VERSION': CACHE_VERSION,
    },
    'redis': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '%s:%s:%s' % (REDIS_HOST, REDIS_PORT, REDIS_DB),
        'OPTIONS': {
            "PARSER_CLASS": "redis.connection.HiredisParser",
        },
        'VERSION': CACHE_VERSION,
    },
}

TORNADO_DEBUG = True
TORNADO_VALIDATE_CERT = True
TORNADO_URL = 'http://127.0.0.1:8888/tornado'
API_GET_STATUS_URL = 'http://127.0.0.1:8000/tasks/%s/'
TORNADO_TIMEOUT = .25 # опрашиваем API 4 раза в секунду

REST_FRAMEWORK = {
    # 'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGE_SIZE': 3
}

EXPORT_KEYS = [
    'TORNADO_URL',
]