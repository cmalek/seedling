#################################################################
# Database Config
#################################################################
from environs import Env

env = Env()
env.read_env()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.str('DB_NAME'),
        'HOST': env.str('DB_HOST'),
        'PORT': env.int('DB_PORT'),
        'USER': env.str('DB_USER'),
        'PASSWORD': env.str('DB_PASSWORD'),
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
            'isolation_level': 'read committed',
        }
    },
}
