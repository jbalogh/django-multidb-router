# A Django settings module to support the tests

TEST_RUNNER = 'django_nose.runner.NoseTestSuiteRunner'

# The default database should point to the master.
DATABASES = {
    'default': {
        'NAME': 'master',
        'ENGINE': 'django.db.backends.sqlite3',
    },
    'slave': {
        'NAME': 'slave',
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

# Put the aliases for slave databases in this list.
SLAVE_DATABASES = ['slave']

# If you use PinningMasterSlaveRouter and its associated middleware, you can
# customize the cookie name and its lifetime like so:
# MULTIDB_PINNING_COOKIE = 'multidb_pin_writes"
# MULTIDB_PINNING_SECONDS = 15
