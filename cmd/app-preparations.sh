#!/bin/bash

# The default behaviour of bash scripts to continue to next commands even if one fails,
# `set -e` makes the script exists if any following commands fails
set -e

echo "Step [1/2] Collecting static files .."
python manage.py collectstatic --noinput

echo "Step [2/2] Applying database migrations .."
python manage.py migrate --noinput
