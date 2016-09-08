#!/usr/bin/env bash

PROJECT_DIR="$HOME/projects/django-tornado-celery-example"
cd ${PROJECT_DIR}

echo "Install the virtual environment.."
source ~/.profile
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv --python=`which python2.7` django-tornado-celery-example
. ~/.virtualenvs/django-tornado-celery-example/bin/activate
make

