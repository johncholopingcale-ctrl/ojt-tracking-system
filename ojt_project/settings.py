"""
Django settings for ojt_project.

OOP Concept Demonstrated: Configuration as Code
This settings file demonstrates how configuration in OOP applications is managed
through class-like structures (dictionaries) and constants. All configuration
is centralized here following the Single Responsibility Principle.

SOLID Principle - Single Responsibility: This file has one job - configuration.
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-ojt-management-system-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.railway.app', '*']

# CSRF trusted origins for production
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost:8000', cast=lambda v: [s.strip() for s in v.split(',')])


# Application definition
# OOP Concept: Each app is a module (package) that encapsulates related functionality
# This demonstrates the principle of Modularity in OOP
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap4',
    'cloudinary_storage',
    'cloudinary',
    # Custom apps - each represents a cohesive module following Single Responsibility
    'accounts',      # User authentication and role management
    'companies',     # Company records and student assignments
    'dtr',          # Daily Time Records
    'journals',     # Weekly journal submissions
    'evaluations',  # Performance evaluations
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ojt_project.urls'

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

WSGI_APPLICATION = 'ojt_project.wsgi.application'


# Database
# OOP Concept: Database Integration - Django ORM maps Python objects to database tables
# This demonstrates how OOP abstracts data persistence
# Database Configuration
# Uses Supabase PostgreSQL if credentials are set, otherwise falls back to SQLite
DB_HOST = config('DB_HOST', default='')

if DB_HOST:
    # Supabase PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='postgres'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': DB_HOST,
            'PORT': config('DB_PORT', default='6543'),
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
else:
    # Local SQLite (for development without Supabase)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# NOTE: Validators disabled for demo purposes - allows simple passwords like "demo" or "1234"
# Re-enable these for production!
AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User uploads)
# OOP Concept: File Handling - Managing user-uploaded files like selfies and profile pictures
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cloudinary Configuration for Production Media Storage
# Railway has ephemeral storage, so we use Cloudinary for persistent media files
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Use Cloudinary in production, local storage in development
if not DEBUG or config('USE_CLOUDINARY', default=False, cast=bool):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
# OOP Concept: Inheritance - Our User model extends Django's AbstractUser
AUTH_USER_MODEL = 'accounts.User'

# Crispy Forms Configuration
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Authentication URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
