#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Django setup
python manage.py collectstatic --no-input --clear
python manage.py migrate --no-input
