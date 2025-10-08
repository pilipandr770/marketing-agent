#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database if needed
# Check if migrations exist, if not create them
if [ ! -d "migrations" ]; then
    flask db init
    flask db migrate -m "Initial migration"
fi

# Run database migrations
flask db upgrade
