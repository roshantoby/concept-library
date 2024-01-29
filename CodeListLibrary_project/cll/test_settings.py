"""
Django settings for testing the CLL project.

Copied from the CLL project settings which were generated by
'django-admin startproject' using Django 1.10.4.

Need to remove the LDAP access for testing so that we can create dummy
users and authenticate them without locking out the test user.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

"""
Django settings for cll project.

For the full list of settings and their values, see
https://docs.djangoproject.com/
"""

import time
from selenium import webdriver

from .settings import *

import os

WEBAPP_HOST = ""

# remote test features
REMOTE_TEST = get_env_value('REMOTE_TEST', cast='bool')
REMOTE_TEST_HOST = 'http://selenium-hub:4444/wd/hub'
IMPLICTLY_WAIT = 10
TEST_SLEEP_TIME = 5

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 'enable'})
chrome_options.accept_insecure_certs = True
chrome_options.accept_ssl_certs = True

# Add your options as needed    
options = [
    "--window-size=1200,1200",
    "--ignore-certificate-errors",
    "--ignore-ssl-errors",
    "--window-size=1280,800",
    "--verbose",
    "--start-maximized",
    "--disable-gpu",
    "--allow-insecure-localhost",
    "--disable-dev-shm-usage",
    "--allow-running-insecure-content",
    # '--headless' #if need debug localy through selenim container comment this line
]

for option in options:
    chrome_options.add_argument(option)

if REMOTE_TEST:
    WEBAPP_HOST = "http://localhost:8000/"
else:
    WEBAPP_HOST = "http://web-test:8000/"

os.environ["DJANGO_SETTINGS_MODULE"] = "cll.test_settings"

# Keep ModelBackend around for per-user permissions and a local superuser.
AUTHENTICATION_BACKENDS = [
    # For testing, we MUST remove the LDAP back-end or the dummy users may
    # cause havoc with the security systems.
    # 'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_value('UNIT_TEST_DB_NAME'),
        'USER': get_env_value('UNIT_TEST_DB_USER'),
        'PASSWORD': get_env_value('UNIT_TEST_DB_PASSWORD'),
        'HOST': get_env_value('UNIT_TEST_DB_REMOTE_HOST') if REMOTE_TEST else get_env_value('UNIT_TEST_DB_HOST'),
        'PORT': '',
        'TEST': {
            'NAME': get_env_value('UNIT_TEST_DB_NAME')  # TODO: check this was cl_testdatabase before!
        },
    }
}

SHOW_COOKIE_ALERT = False
