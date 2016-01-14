"""
Django settings for newyearapi project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

try:
    os.makedirs(LOG_DIR)
except:
    pass

ADMINS = (
    ('Xindong Ding', 'dxd.spirits@gmail.com'),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f^mv=5w3_+6fl=a0qed(z5-ij-g@@9o#dh79xj5e6442am^yf^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'suit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',

    'greetings'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'helper.middlewares.MethodOverrideMiddleware'
)

ROOT_URLCONF = 'newyearapi.urls'

WSGI_APPLICATION = 'newyearapi.wsgi.application'

# Templates

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
                'django.template.context_processors.request',
            ],
        },
    },
]

# Rest framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        'users.authentication.TokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
        # 'rest_framework.renderers.AdminRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
}

REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,  # 3600 seconds = 1 hour
    'DEFAULT_LIST_CACHE_KEY_FUNC': 'helper.drf.fixed_list_cache_key_func',
}

# CORS

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'cache-control',
    'x-http-method-override'
)

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] "%(levelname)s %(module)s" %(message)s',
            'datefmt': '%d/%b/%Y %I:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            # 'include_html': True,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(LOG_DIR, 'apps.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'apps': {
            'handlers': ['mail_admins', 'log_file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

import codecs
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'newyear',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'users': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'teteatete',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

DATABASE_ROUTERS = ['users.routers.UsersRouter']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'
# LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True
USE_L10N = False
USE_TZ = False

DATE_FORMAT = 'Y-m-d'
TIME_FORMAT = 'H:i:s'
DATETIME_FORMAT = 'Y-m-d H:i:s'

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Email and SMS

SERVER_EMAIL = 'api@wedfairy.com'
EMAIL_HOST = 'smtp.ym.163.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'api@wedfairy.com'
EMAIL_HOST_PASSWORD = '********'

SMS_OFF = DEBUG

# Wechat

WECHAT_APP = {
    'composer': {
        'APP_ID': '',
        'APP_SECRET': ''
    },
    'hybrid': {
        'APP_ID': '',
        'APP_SECRET': ''
    },
}

REDIS = {
    'host': '127.0.0.1',
    'port': 6379,
    'user': '',
    'pwd': '',
    'password': ''
}

# Local settings

try:
    LOCAL_SETTINGS  # @UndefinedVariable
except NameError:
    try:
        from settings_local import *  # @UnusedWildImport
    except ImportError:
        pass
