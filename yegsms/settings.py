"""
Django settings for yegsms project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
import dj_database_url
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import os.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*us=$0&+m!=5lh*!%ihzpi_5)tifeep4+24p6_b)#_!$c@+jhu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_twilio',
    'dj_database_url',
    'sms',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'yegsms.urls'

WSGI_APPLICATION = 'yegsms.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
)

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Parse database configuration from $DATABASE_URL
#DATABASES['default'] =  dj_database_url.config()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dbiup6i64tv78k',
        'USER': 'uosqriiqcifbbi',
        'PASSWORD': 'td-3wwLgTE--lNSkKAfNlTM-Q8',
        'HOST': 'ec2-107-21-104-188.compute-1.amazonaws.com',
        'PORT': '5432',
    }
}
#DATABASES = {'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))}
#DATABASES['default'] = 

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates').replace('\\','/'),
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static').replace('\\','/'),
)

LOGIN_REDIRECT_URL='/dashboard/'

TWILIO_ACCOUNT_SID = 'ACaca92adf5b074dad31e78b705e5a1d30'
TWILIO_AUTH_TOKEN = 'ffb68cdb782d127c3958cfe9bac5d03c'
