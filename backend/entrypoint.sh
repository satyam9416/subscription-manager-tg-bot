#!/bin/bash

echo "Waiting for database to be ready..."
sleep 10
echo "Database should be ready!"

echo "Applying database migrations..."

# Reset migrations and recreate
echo "Resetting migrations..."
flask db stamp head
flask db upgrade

echo "Starting Flask application..."
exec python run.py