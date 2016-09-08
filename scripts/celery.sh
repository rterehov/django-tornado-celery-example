#!/usr/bin/env bash
PROJECT_DIR="$HOME/projects/django-tornado-celery-example"
cd ${PROJECT_DIR}

. ~/.virtualenvs/django-tornado-celery-example/bin/activate
./manage.py celery worker -c 5 --settings=main.vagrant