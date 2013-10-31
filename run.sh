#!/bin/bash

export PYTHONPATH=".:$PYTHONPATH"
export DJANGO_SETTINGS_MODULE="test_settings"

usage() {
    echo "USAGE: $0 [command]"
    echo "  test - run the tests"
    echo "  shell - open the Django shell"
    echo "  check - run flake8"
    exit 1
}

case "$1" in
    "test" )
        django-admin.py test multidb ;;
    "shell" )
        django-admin.py shell ;;
    "check" )
        flake8 multidb ;;
    * )
        usage ;;
esac
