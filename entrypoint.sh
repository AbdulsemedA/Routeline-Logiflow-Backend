#!/bin/bash
set -e

# Run initialization only if we are starting the web server
if [ "$1" = "daphne" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput

    echo "Applying database migrations..."
    python manage.py migrate --noinput
fi

# Execute the container's main process
exec "$@"
