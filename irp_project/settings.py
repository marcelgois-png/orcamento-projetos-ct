from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# SECRET_KEY: em produção (DEBUG=False) é obrigatória — falha cedo se ausente.
# Em desenvolvimento aceita um fallback claramente inseguro.
if DEBUG:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-only-troque-em-producao')
else:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError(
            'SECRET_KEY não definida. Configure a variável de ambiente SECRET_KEY antes de rodar com DEBUG=False.'
        )

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '*' if DEBUG else '').split(',') if h.strip()]

# CSRF: domínios confiáveis para POSTs vindos de HTTPS atrás do proxy.
# Sem isso, Django 4+ rejeita formulários em produção.
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_htmx',
    'core',
    'orcamento',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'irp_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'irp_project.wsgi.application'

if os.environ.get('DJANGO_USE_SQLITE') == '1':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'irp_db'),
            'USER': os.environ.get('DB_USER', 'irp_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            # Reusa conexões entre requests (perf significativa com gunicorn)
            'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
            'CONN_HEALTH_CHECKS': True,
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Recife'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Cache busting de estáticos: cada deploy invalida o cache do navegador automaticamente.
# Em DEBUG usa o storage default (sem hashing) para não travar dev.
if not DEBUG:
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'},
    }

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024 + 65536
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000  # forms grandes (planilhas, lotes)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

X_FRAME_OPTIONS = 'DENY'

# ── Segurança em produção (ativa quando DEBUG=False) ──────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Lax'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/modulos/'
LOGOUT_REDIRECT_URL = '/login/'

# ── E-mail ────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'IRP CT/UFPB <noreply@ct.ufpb.br>')

PASSWORD_RESET_TIMEOUT = 86400

# ── Logging ───────────────────────────────────────────────────────────────────
# Em produção: console (capturado pelo gunicorn/docker) + arquivo rotativo (se LOG_DIR existir).
LOG_DIR = os.environ.get('LOG_DIR', str(BASE_DIR / 'logs'))
_log_handlers_root = ['console']
_log_handlers_app = ['console']
_log_handlers_django = ['console']

_file_logging_handlers = {}
if not DEBUG and LOG_DIR:
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        _file_logging_handlers = {
            'app_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'app.log'),
                'maxBytes': 10 * 1024 * 1024,
                'backupCount': 5,
                'formatter': 'verbose',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'error.log'),
                'maxBytes': 10 * 1024 * 1024,
                'backupCount': 10,
                'formatter': 'verbose',
            },
        }
        _log_handlers_root += ['error_file']
        _log_handlers_app += ['app_file', 'error_file']
        _log_handlers_django += ['app_file', 'error_file']
    except OSError:
        # Falha em criar o diretório de logs não deve impedir a app de subir
        pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {process:d} {thread:d} - {message}',
            'style': '{',
        },
        'simple': {'format': '{levelname} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'},
        **_file_logging_handlers,
    },
    'root': {
        'handlers': _log_handlers_root,
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': _log_handlers_django,
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': _log_handlers_app,
            'level': 'WARNING',
            'propagate': False,
        },
        'core': {'handlers': _log_handlers_app, 'level': 'INFO', 'propagate': False},
        'orcamento': {'handlers': _log_handlers_app, 'level': 'INFO', 'propagate': False},
    },
}

# ── Sentry (opcional — ativa apenas se SENTRY_DSN definido) ────────────────────
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
if SENTRY_DSN and not DEBUG:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
            send_default_pii=False,
            environment=os.environ.get('SENTRY_ENVIRONMENT', 'production'),
            release=os.environ.get('SENTRY_RELEASE', ''),
        )
    except ImportError:
        sys.stderr.write('SENTRY_DSN definido mas sentry-sdk não instalado.\n')
