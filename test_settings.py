# A Django settings module to support the tests

SECRET_KEY = 'dummy'
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware'
)

# The default database should point to the read/write primary.
DATABASES = {
    'default': {
        'NAME': 'primary.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
    },
    'replica': {
        'NAME': 'replica.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

# Put the aliases for replica databases in this list.
REPLICA_DATABASES = ['replica']

# If you use PinningReplicaRouter and its associated middleware, you can
# customize the cookie name and its lifetime like so:
# MULTIDB_PINNING_COOKIE = "multidb_pin_writes"
# MULTIDB_PINNING_SECONDS = 15
