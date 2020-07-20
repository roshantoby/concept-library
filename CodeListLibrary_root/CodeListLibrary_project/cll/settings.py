"""
Django settings for cll project.

For the full list of settings and their values, see
https://docs.djangoproject.com/
"""

import os
import ldap
import sys
import socket

from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, NestedActiveDirectoryGroupType, LDAPSearchUnion
from django.conf.global_settings import EMAIL_BACKEND, AUTHENTICATION_BACKENDS
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages import constants as messages

from decouple import Config, RepositoryEnv, Csv

from django.core.exceptions import ImproperlyConfigured
import distutils
from distutils import util


def GET_SERVER_IP():
    """
        returns the server IP
    """
    S = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        S.connect(('10.255.255.255', 1))
        IP = S.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        S.close()
    return IP

SRV_IP = GET_SERVER_IP()  

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# This is for DEMO server only since it is configured in a different way
IS_DEMO = False
def chk_IS_DEMO():
    try:
        return bool(distutils.util.strtobool(os.environ["IS_DEMO"]))       
    except KeyError:
        try:
            DOTINI_FILE = BASE_DIR  + "/cll/.ini"
            env_config = Config(RepositoryEnv(DOTINI_FILE))
            return env_config.get("IS_DEMO", cast=bool)
        except KeyError:
            error_msg = 'Set the IS_DEMO environment variable !!'
            raise ImproperlyConfigured(error_msg)

        
IS_DEMO = chk_IS_DEMO()
#print IS_DEMO
    
def get_env_value(env_variable , cast = None):
    try:
        if IS_DEMO: # Demo non-docker    
            # separate settings for different environments
            DOTINI_FILE = BASE_DIR  + "/cll/.ini"
            env_config = Config(RepositoryEnv(DOTINI_FILE))
            if cast == 'bool':
                return env_config.get(env_variable, cast=bool)
            else:
                return env_config.get(env_variable)
        else:
            if cast == None:
                return os.environ[env_variable]
            elif cast == 'int':
                return int(os.environ[env_variable])
            elif cast == 'bool':
                return bool(distutils.util.strtobool(os.environ[env_variable]))
            else:
                return os.environ[env_variable]        
    except KeyError:
        error_msg = 'Set the {} environment variable'.format(env_variable)
        raise ImproperlyConfigured(error_msg)
    

# check OS
IS_LINUX = False
if os.name.lower()=="nt":
    path_prj = BASE_DIR    # windows os
    IS_LINUX = False
else:
    path_prj = BASE_DIR    # Linux 
    IS_LINUX = True
    
if path_prj not in sys.path:
    sys.path.append(path_prj)
    
#==========================================================================
# separate settings for different environments
#general variables
CLL_READ_ONLY =  get_env_value('CLL_READ_ONLY', cast='bool')
ENABLE_PUBLISH = get_env_value('ENABLE_PUBLISH', cast='bool')
SHOWADMIN  = get_env_value('SHOWADMIN', cast='bool')
BROWSABLEAPI = get_env_value('BROWSABLEAPI', cast='bool')

IS_INSIDE_GATEWAY = get_env_value('IS_INSIDE_GATEWAY', cast='bool')
IS_DEVELOPMENT_PC = get_env_value('IS_DEVELOPMENT_PC', cast='bool')
if IS_DEVELOPMENT_PC:
    print "SRV_IP=" + SRV_IP


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_value('SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env_value('DEBUG', cast='bool')


        
ADMIN = [('Muhammad', 'Muhammad.Elmessary@Swansea.ac.uk'), ('Dan', 'd.s.thayer@swansea.ac.uk')]
ALLOWED_HOSTS = [ 'localhost', '127.0.0.1'
                ]
ALLOWED_HOSTS_env = get_env_value('ALLOWED_HOSTS').split(",")
ALLOWED_HOSTS_env = map(lambda v: v.strip() , ALLOWED_HOSTS_env)

ALLOWED_HOSTS = ALLOWED_HOSTS + ALLOWED_HOSTS_env
ALLOWED_HOSTS = list(set(ALLOWED_HOSTS))
#print ALLOWED_HOSTS



ROOT_URLCONF = 'cll.urls'
DATA_UPLOAD_MAX_MEMORY_SIZE = None


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CLINICALCODE_SESSION_ID = 'concept'

#===========================================================================
    
os.environ["DJANGO_SETTINGS_MODULE"] = "cll.settings"


# Static files (CSS, JavaScript, Images) 
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'cll/static'), ]

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticroot')

WSGI_APPLICATION = 'cll.wsgi.application'


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# Binding and connection options
# LDAP authentication  =======================================================get_env_value('')
AUTH_LDAP_SERVER_URI = get_env_value('AUTH_LDAP_SERVER_URI')
AUTH_LDAP_BIND_DN = get_env_value('AUTH_LDAP_BIND_DN')

AUTH_LDAP_BIND_PASSWORD = get_env_value('AUTH_LDAP_BIND_PASSWORD')   

AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
    LDAPSearch(get_env_value('AUTH_LDAP_USER_SEARCH'), ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)"),
)
    
# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(get_env_value('AUTH_LDAP_GROUP_SEARCH'), ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)")
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

# Simple group restrictions
AUTH_LDAP_REQUIRE_GROUP = get_env_value('AUTH_LDAP_REQUIRE_GROUP')

# Populate the django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
#==============================================================================


# Application definition
INSTALLED_APPS = []
if SHOWADMIN:
    INSTALLED_APPS = INSTALLED_APPS + ['django.contrib.admin', ]
    
INSTALLED_APPS = INSTALLED_APPS + [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mathfilters',
    'clinicalcode',
    'cll',
    'simple_history',
    'rest_framework',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # manages sessions across requests
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # associates users with requests using sessions
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    
    'cll.middleware.brandMiddleware'
]

# Keep ModelBackend around for per-user permissions and a local superuser.
# Don't check AD on development PCs due to network connection
if IS_DEVELOPMENT_PC: 
    AUTHENTICATION_BACKENDS = [
    #    'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
    ]
else:  
    AUTHENTICATION_BACKENDS = [
        'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
    ]

                          
REST_FRAMEWORK = {
#     'DEFAULT_RENDERER_CLASSES': (
#         'rest_framework.renderers.JSONRenderer',
#         'rest_framework_xml.renderers.XMLRenderer',
#         'rest_framework.renderers.BrowsableAPIRenderer',  
#     ), 
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}


if not BROWSABLEAPI:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] =  (
                                                    'rest_framework.renderers.JSONRenderer',
                                                    'rest_framework_xml.renderers.XMLRenderer',
                                                )  


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cll.context_processors.general_var',
            ],
        },
    },
]


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_value('DB_NAME'),
        'USER': get_env_value('DB_USER'),
        'PASSWORD': get_env_value('DB_PASSWORD'),
        'HOST': get_env_value('DB_HOST'),
        'PORT': '',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

if IS_LINUX:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            },
        },
    }
else:    
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
                'filename': os.path.join(BASE_DIR, 'debug.log'),
            },
            'stream_to_console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler'
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'django_auth_ldap': {
                'handlers': ['stream_to_console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }



GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
}



# Redirect to home URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = reverse_lazy('concept_list')
LOGIN_URL = reverse_lazy('login')
LOGOUT_URL = reverse_lazy('logout')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

CURRENT_BRAND = ""
CURRENT_BRAND_WEBSITE = ""

if not DEBUG:
    SESSION_COOKIE_AGE = 3600       # 1 hour

DEV_PRODUCTION = ""
if IS_DEMO:  # Demo server
    DEV_PRODUCTION = "<i class='glyphicon glyphicon-cog'> </i>DEMO SITE<i class='glyphicon glyphicon-cog'> </i>"
 
  