import ast
import os
from django.utils.translation import gettext_lazy as _
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))

SECRET_KEY = '@u$pb9@k)qq^b@_mx2%h$a0ss23r@!8*23i4mh(8x$v=q)1%7r5j'


def get_list(text):
    return [item.strip() for item in text.split(',')]


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as err:
            raise ValueError(
                '{} is an invalid value for {}'.format(value, name)) from err
    return default_value


DEBUG = get_bool_from_env('DEBUG', True)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'django_celery_results',
    'django_celery_beat',
    'constance',
    'constance.backends.database',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_yasg',
    'wms_local',
    'wms_local.account',
    'wms_local.core'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'wms_local.urls'

context_processors = [
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.debug',
    'django.template.context_processors.i18n',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.template.context_processors.request',
    'constance.context_processors.config',
]

loaders = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader']

if not DEBUG:
    loaders = [('django.template.loaders.cached.Loader', loaders)]
    # integration sentry
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
    )

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'OPTIONS': {
        'debug': DEBUG,
        'context_processors': context_processors,
        'loaders': loaders,
    }}]


ENABLE_DEBUG_TOOLBAR = get_bool_from_env("ENABLE_DEBUG_TOOLBAR", False)
if ENABLE_DEBUG_TOOLBAR:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    INSTALLED_APPS.append("debug_toolbar")
    DEBUG_TOOLBAR_PANELS = [
        # adds a request history to the debug toolbar
        "ddt_request_history.panels.request_history.RequestHistoryPanel",
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ]
    INTERNAL_IPS = ['127.0.0.1']
    DEBUG_TOOLBAR_CONFIG = {"RESULTS_CACHE_SIZE": 100}

# CONFIG silk-django
ENABLE_SILK = get_bool_from_env('ENABLE_SILK', False)
if ENABLE_SILK:
    MIDDLEWARE.insert(0, 'silk.middleware.SilkyMiddleware')
    INSTALLED_APPS.append('silk')

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('vi', _('Vietnamese')),
]

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = False

USE_L10N = True

USE_TZ = False

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
if not os.path.isdir(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = "https://s.giaohangtietkiem.vn/wms_static/"

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
]

AUTH_USER_MODEL = 'account.User'
LOGIN_URL = 'account:login'
LOGOUT_URL = 'account:logout'
LOGIN_REDIRECT_URL = 'home'

# CONFIG DASHBOARD
DASHBOARD_PAGINATE_BY = 30
DASHBOARD_SEARCH_LIMIT = 5
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# CELERY SETTINGS
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
if os.environ.get("CELERY_REDIS_TYPE") == "sentinel":
    CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600, "master_name": "redis-cluster"}
CELERY_TASK_ALWAYS_EAGER = not CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
DJANGO_CELERY_BEAT_TZ_AWARE = False

# DRF & CORS
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50,
}

# SWAGGER
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'DOC_EXPANSION': 'none',
    'DEFAULT_MODEL_RENDERING': 'example',
    'USE_SESSION_AUTH': True
}

ALLOWED_HOSTS = ["*"]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CACHES
if os.environ.get("CELERY_REDIS_TYPE") == "sentinel":
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ.get("CACHE_REDIS"),
            "OPTIONS": {
                "PASSWORD": os.environ.get("CACHE_REDIS_PASS"),
                "CLIENT_CLASS": "django_sentinel.SentinelClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ.get("CACHE_REDIS"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient"
            },
        }
    }

DATABASE_URI = os.environ.get(
    'DATABASE_URI') or "mysql://tuandv:d6b8cc42803ea100735@10.130.64.22:3306/wms_local?charset=utf8"
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URI,
        conn_max_age=600)
}
