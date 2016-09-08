#!/usr/bin/env bash

PROJECT_ROOT=/home/vagrant/projects/django-tornado-celery-example/

echo "Start Django server"
screen -S django -d -m su - vagrant $PROJECT_ROOT/scripts/django.sh

echo "Start tornado server"
screen -S tornado -d -m su - vagrant $PROJECT_ROOT/scripts/tornado.sh

echo "Start celery"
screen -S celery -d -m su - vagrant $PROJECT_ROOT/scripts/celery.sh
