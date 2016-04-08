## Copyright 2012 Raik Gruenberg

## This file is part of the labhamster project (http://labhamster.sf.net)
## Labhamster is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.

## Labhamster is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.

## You should have received a copy of the GNU Affero General Public
## License along with labhamster. If not, see <http://www.gnu.org/licenses/>.

DEBUG = True
TEMPLATE_DEBUG = True
ADMINS = ()
MANAGERS = ADMINS

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/home/raik/data/py/labhamsterproject/labhamster.db',
             'USER': '',
             'PASSWORD': '',
             'HOST': '',
             'PORT': ''}}

TIME_ZONE = 'America/Montreal'

LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = False

DATE_FORMAT = 'y-m-d'

MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATICFILES_DIRS = ()
STATICFILES_FINDERS = ('django.contrib.staticfiles.finders.FileSystemFinder', 
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder')

## change!!
SECRET_KEY = 'x7n$dfemj-#+@(!=t@#&6$h*uc$(x(j4bve$4@+i)5uau!#x&8'

TEMPLATE_LOADERS = ('django.template.loaders.app_directories.Loader',
                    'django.template.loaders.filesystem.Loader')

MIDDLEWARE_CLASSES = ('django.middleware.common.CommonMiddleware',
                      'django.contrib.sessions.middleware.SessionMiddleware',
                      'django.middleware.csrf.CsrfViewMiddleware',
                      'django.contrib.auth.middleware.AuthenticationMiddleware',
                      'django.contrib.messages.middleware.MessageMiddleware')

ROOT_URLCONF = 'urls'
TEMPLATE_DIRS = ()

INSTALLED_APPS = ('django.contrib.admin',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.messages',
                  'django.contrib.staticfiles',
                  'labhamster')

LOGGING = {'version': 1,
           'disable_existing_loggers': False,
           
           ## slashdot hint: http://stackoverflow.com/questions/1598823/elegant-setup-of-python-logging-in-django
           'filters': {
               'require_debug_false': {
                   '()': 'django.utils.log.RequireDebugFalse'
               }
           },          

           'handlers': {'mail_admins': 
                        {'level': 'ERROR',
                         'filters': ['require_debug_false'], 
                         'class': 'django.utils.log.AdminEmailHandler'}
                        },
           'loggers': {'django.request': {'handlers': ['mail_admins'],
                                          'level': 'ERROR',
                                          'propagate': True}}}
