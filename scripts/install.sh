#!/usr/bin/env bash

PROJECT_DIR=/home/vagrant/projects/django-tornado-celery-example

echo "Install libs..."
sudo apt-get update -y
# sudo apt-get autoremove -y
sudo apt-get install -y libxml2-dev libxslt-dev redis-server git \
    python-dev python-pip libffi-dev libfreetype6 libfreetype6-dev \
    zlib1g zlib1g-dev libmemcached-dev libssl-dev build-essential
sudo pip install virtualenv virtualenvwrapper

echo "Install the virtual environment.."
sudo su - vagrant /bin/bash -c 'echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.profile'
sudo su - vagrant /bin/bash -c 'echo "export PROJECT_HOME=$HOME/Devel" >> ~/.profile'