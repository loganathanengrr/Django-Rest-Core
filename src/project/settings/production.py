import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


TEMPLATE_DIR =os.path.join(BASE_DIR,'templates')


SECRET_KEY = 'vp05gf8j#7q#9*@zqdz*#w=(uihex0ijgy^f=y_*=qklyf)eqj'


DEBUG = False


ADMINS = (
)


MANAGERS = ADMINS


ALLOWED_HOSTS = ['*']


EMAIL_HOST = os.environ.get('EMAIL_HOST','')


EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER','')


EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD','')


EMAIL_PORT = 587


EMAIL_USE_TLS = True


DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


STATIC_URL = '/static/'


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]


STATIC_ROOT = os.path.join(BASE_DIR, "static/")


MEDIA_ROOT =os.path.join(BASE_DIR,"media/")


MEDIA_URL = '/media/'


FIXTURE_DIRS = (
   os.path.join(BASE_DIR,"api/fixtures/"),
)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'storages',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'django_celery_beat',
    'django_celery_results',

    'accounts',
    'analytics',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'


AUTH_USER_MODEL  = 'accounts.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR,],
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



WSGI_APPLICATION = 'project.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME','core'),
        'USER': os.environ.get('DB_USER','postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD',''),
        'HOST': os.environ.get('DB_HOST','localhost'),
        'PORT': '',
    }
}


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


DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', # '2006-10-25', '10/25/2006', '10/25/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
    ]


DATA_UPLOAD_MAX_NUMBER_FIELDS = 50000


LANGUAGE_CODE = 'en-us'


TIME_ZONE = 'UTC'


USE_I18N = True


USE_L10N = True


USE_TZ = True


SEND_ACTIVATION_EMAIL  = False


USER_EMAIL_FIELD_NAME  = 'email'


PASSWORD_RESET_CONFIRM_URL     = '#password-reset/{uid}/{token}'


ACTIVATION_URL         = '#activate/{uid}/{token}'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


from project.corsconf import *


from project.rest_conf import *


from project.aws import *


CELERY_BROKER_URL = 'redis://localhost:6379'


CELERY_RESULT_BACKEND = 'django-db'


CELERY_ACCEPT_CONTENT = ['application/json']


CELERY_TASK_SERIALIZER = 'json'


CELERY_RESULT_SERIALIZER = 'json'


CELERY_TIMEZONE = TIME_ZONE


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console']},
    'formatters': {
        'verbose': {
            'format': (
                '%(levelname)s %(name)s %(message)s'
                ' [PID:%(process)d:%(threadName)s]')},
        'simple': {
            'format': '%(levelname)s %(message)s'}},
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'}},
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'},
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'},
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, "dubug.log")}},
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins','file'],
            'level': 'INFO',
            'propagate': True},
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True},
        'project': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True}}}
