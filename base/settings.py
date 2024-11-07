"""
Django settings for base project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import json, os
from pathlib import Path
from django.contrib.messages import constants as messages


with open('secrets.json') as f:
    secrets = json.load(f)
    DATABASES = secrets['DATABASES']
    DEBUG = secrets['DEBUG']
    EMAIL_HOST = secrets['EMAIL_HOST']
    EMAIL_HOST_USER = secrets['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = secrets['EMAIL_HOST_PASSWORD']

    PWA_APP_NAME = secrets['PWA_APP_NAME']
    PWA_APP_DESCRIPTION = secrets['PWA_APP_DESCRIPTION']
    PWA_APP_THEME_COLOR = secrets['PWA_APP_THEME_COLOR']
    PWA_APP_BACKGROUND_COLOR = secrets['PWA_APP_BACKGROUND_COLOR']
    PWA_APP_DISPLAY = secrets['PWA_APP_DISPLAY']
    PWA_APP_SCOPE = secrets['PWA_APP_SCOPE']
    PWA_APP_ORIENTATION = secrets['PWA_APP_ORIENTATION']
    PWA_APP_START_URL = secrets['PWA_APP_START_URL']
    PWA_APP_STATUS_BAR_COLOR = secrets['PWA_APP_STATUS_BAR_COLOR']
    VAPID_PUBLIC_KEY = secrets['VAPID_PUBLIC_KEY']
    VAPID_PRIVATE_KEY = secrets['VAPID_PRIVATE_KEY']
    VAPID_ADMIN_EMAIL = secrets['VAPID_ADMIN_EMAIL']
    WEBPUSH_HABILITADO = secrets['WEBPUSH_HABILITADO']
    HABILITADO_FIREBASE = secrets.get('HABILITADO_FIREBASE', False)
    FIREBASE_BUCKET_NAME = secrets['FIREBASE_BUCKET_NAME']
    TINYMCE_IMAGES_FOLDER = secrets['TINYMCE_IMAGES_FOLDER']
    FIREBASE_IMAGES_FOLDER = secrets['FIREBASE_IMAGES_FOLDER']
    
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-eaz962(bu!_=sht)zx3*qncu-^x5852y=-ljklivuy+f+sot!^'
# DEBUG = True

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.postgres',

    'django.contrib.flatpages',

    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',

    'nested_admin',
    'mptt',
    'pwa',
    'webpush',
    'tinymce',
    'django_social_share',
    'cropperjs',

    'applications.core',
    'applications.main',
    'applications.administracion',
    'applications.blog',

    'django_tables2',
    'crudbuilder',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # allauth
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates', BASE_DIR / 'applications' / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'applications.core.context_processors.main_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'base.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'example',
#         'USER': 'example',
#         'PASSWORD': 'example',
#         'HOST': 'example',
#         'PORT': 'example',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_ROOT = BASE_DIR / 'static'
STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'staticfiles', BASE_DIR / 'applications' / 'staticfiles' ]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# **************************************************************
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'example@gmail.com'
# EMAIL_HOST_PASSWORD = 'example'

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_LOGOUT_ON_GET = True

LOGIN_REDIRECT_URL = 'core:my_usuario'
AUTH_USER_MODEL = 'core.CustomUser'

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# Tinymce ***********************************************
TINYMCE_COMPRESSOR = False

TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "height": 250,
    "menubar": False,
    "plugins": "advlist,autolink,lists,link,image,charmap,print,preview,anchor,"
    "searchreplace,visualblocks,code,fullscreen,insertdatetime,media,table,paste,"
    "code,help,wordcount",
    "external_plugins": {
        "tiny_mce_wiris": 'https://www.wiris.net/demo/plugins/tiny_mce/plugin.min.js',                  
    },
    "toolbar": "undo redo | formatselect | image code | "
    "bold italic | alignleft aligncenter superscript subscript charmap "
    "alignright alignjustify | bullist numlist outdent indent | "
    "tiny_mce_wiris_formulaEditor tiny_mce_wiris_formulaEditorChemistry"
    "removeformat | help",
    "images_upload_url": "/upload_image/",
    # "document_base_url": "https://goeducativa.com/",
    "relative_urls": False,
    "convert_urls": False,
    # "paste_as_text": True,
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880 # 5 MB

SECURE_CROSS_ORIGIN_OPENER_POLICY='same-origin-allow-popups'
SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'


# **************************************************************
# Webpush
# **************************************************************
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": VAPID_PUBLIC_KEY,
    "VAPID_PRIVATE_KEY": VAPID_PRIVATE_KEY,
    "VAPID_ADMIN_EMAIL": VAPID_ADMIN_EMAIL
}

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
}


USUARIOS_ADMIN = ['juanbacan']


# PWA_APP_NAME = 'CACES'
# PWA_APP_DESCRIPTION = "CACES"
# PWA_APP_THEME_COLOR = '#0A0302'
# PWA_APP_BACKGROUND_COLOR = '#ffffff'
# PWA_APP_DISPLAY = 'standalone'
# PWA_APP_SCOPE = '/'
# PWA_APP_ORIENTATION = 'any'
# PWA_APP_START_URL = '/'
# PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
        'src': '/static/images/logos/logo_160_160.png',
        'sizes': '160x160'
    }
]
PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/images/logos/logo_160_160.png',
        'sizes': '160x160'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/images/logos/logo_160_160.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'es-ES'
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'static', 'assets', 'js', 'serviceworker.js')


if HABILITADO_FIREBASE:
    print("Cargando Firebase")
    import firebase_admin
    from firebase_admin import credentials

    cred = credentials.Certificate(BASE_DIR / 'firebase.json')
    firebase_admin.initialize_app(cred)