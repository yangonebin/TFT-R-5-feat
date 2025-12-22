from pathlib import Path
import os
from datetime import timedelta

# 1. 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. 보안 설정
SECRET_KEY = 'django-insecure-#yu@2oxzo=v^_^g*zp@vz6ds6fas$26!lxvxiccp4!ukkoyqch'
DEBUG = True
ALLOWED_HOSTS = []

# 3. 애플리케이션 정의
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third Party Apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework_simplejwt',

    # Local Apps
    'accounts',
    'articles',
    'finlife',
]

# 4. 미들웨어 설정
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# 5. CORS 설정
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

# 6. REST Framework 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny', # 초기 개발 편의를 위해 수정
    ),
}

# 7. JWT 및 dj-rest-auth 상세 설정
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False,
    'JWT_AUTH_COOKIE': 'my-app-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'my-refresh-token',
    'REGISTER_SERIALIZER': 'accounts.serializers.CustomRegisterSerializer',
    'USER_DETAILS_SERIALIZER': 'accounts.serializers.CustomUserDetailSerializer',
}

# 8. Allauth 상세 설정 (비밀번호 확인 및 이메일 제거 핵심)
SITE_ID = 1
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
ACCOUNT_LOGIN_METHODS = {'username'}
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'

# [핵심] password2 에러 방지를 위해 두 번 입력을 True로 설정 (프론트엔드와 일치시킴)
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True 

# 9. Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# 10. URL 및 템플릿 설정
ROOT_URLCONF = 'final_pjt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'final_pjt.wsgi.application'

# 11. 데이터베이스 설정
DB_PATH = BASE_DIR.parent / 'service_data.db'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}

# 12. [중요] 비밀번호 검증기 제거 (테스트 시 '너무 쉬운 비번'으로 가입 가능하게 함)
AUTH_PASSWORD_VALIDATORS = []

# 13. 공통 설정
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}