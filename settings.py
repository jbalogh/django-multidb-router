# An illustrative example settings.py.  You need to define DATABASES and
# SLAVE_DATABASES.


# The default database should point to the master.
DATABASES = {
    'default': {
        'NAME': 'master',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '',
        'PORT': '',
        'USER': '',
        'PASSWORD': '',
        'OPTIONS': {'init_command': 'SET storage_engine=InnoDB'},
    },
    'slave': {
        'NAME': 'slave',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '',
        'PORT': '',
        'USER': '',
        'PASSWORD': '',
        'OPTIONS': {'init_command': 'SET storage_engine=InnoDB'},
    },
}

# Put the aliases for slave databases in this list.
SLAVE_DATABASES = ['slave']
