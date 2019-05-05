"""
Django settings for VSWarehouse project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "WAREHOUSE_SECRET_KEY",
    '2av#z%lmbq#n=*+!5y=i&!pak5ei!!0*$w5#2kf_#%an8ept@_'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("WAREHOUSE_DEBUG", "TRUE") == "TRUE"

if not DEBUG:
    ALLOWED_HOSTS = os.getenv("WAREHOUSE_HOSTS", '*').split(",")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'fullurl',

    'warehouse',
    'simple',
    'frontend'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'VSWarehouse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'VSWarehouse.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

driver = os.environ.get("DB_ENGINE", "sqlite3")
if driver == "sqlite3":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',

            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
elif driver == "mysql":
    import platform
    if platform.system() == "Windows":
        import pymysql
        pymysql.install_as_MySQLdb()

    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.mysql',

        'NAME':     os.getenv('MYSQL_DATABASE'),
        'USER':     os.getenv('MYSQL_USER'),
        'HOST':     os.getenv('MYSQL_HOST'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD'),
        'PORT':     os.getenv('MYSQL_PORT',    3306)
    }}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = __file__ + "/../../static"
