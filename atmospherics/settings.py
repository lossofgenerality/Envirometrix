"""
Django settings for atmospherics project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import djcelery
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

# Celery settings
BROKER_URL = 'amqp://guest@localhost:5672//'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json','pickle']
CELERY_RESULT_BACKEND='amqp'
CELERY_ACKS_LATE = True
CELERY_IGNORE_RESULT = False
CELERY_DEFAULT_QUEUE = 'atmospherics'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/django-atmospherics.log',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'trading.models':{
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'REDACTED FOR SECURITY REASONS'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages'
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'djcelery',
    'dajaxice',
    'logger',
    'data',
    'analysis',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'atmospherics.urls'

WSGI_APPLICATION = 'atmospherics.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',                           # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'atmospherics',                                                 # Or path to database file if using sqlite3.
        'USER': 'REDACTED FOR SECURITY REASONS',               # Not used with sqlite3.
        'PASSWORD': 'REDACTED FOR SECURITY REASONS',      # Not used with sqlite3.
        'HOST': 'localhost',                                                        # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                                                                     # Set to empty string for default. Not used with sqlite3.
        #'autocommit': True,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/accounts/login/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (
  os.path.join(SITE_ROOT, 'static/'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'dajaxice.finders.DajaxiceFinder',
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
    os.path.join(BASE_DIR, 'analysis/templates'),
)

EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_HOST_USER = 'REDACTED FOR SECURITY REASONS'
EMAIL_HOST_PASSWORD = 'REDACTED FOR SECURITY REASONS'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

SSH_HOST = 'REDACTED FOR SECURITY REASONS'
SSH_USER = 'REDACTED FOR SECURITY REASONS'
SSH_PASSWORD = 'REDACTED FOR SECURITY REASONS'

#Copyright 2014 Thorek/Scott and Partners. All Rights Reserved.


#Copyright 2014-present lossofgenerality.com
#License: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html