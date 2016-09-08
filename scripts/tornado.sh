#!/usr/bin/env bash
PROJECT_DIR="$HOME/projects/django-tornado-celery-example"
cd ${PROJECT_DIR}

. ~/.virtualenvs/django-tornado-celery-example/bin/activate
./manage.py tornado-start 0.0.0.0:8888 --settings=main.vagrant
