#!/usr/bin/env bash
# eecho "🚀 Applying database migrations..."
# Run migrations (will create/update tables)
flask db upgrade

echo "🔧 Applying manual migration for LinkedIn and Meta fields..."
# Apply manual SQL migration via Flask CLI (idempotent - safe to run multiple times)
flask apply-manual-migration

echo "✅ Build completed successfully!"n error
set -o errexit

echo "🔧 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️ Setting up database migrations..."

# Check if migrations directory exists
if [ ! -d "migrations" ]; then
    echo "📁 Migrations directory not found - initializing..."
    flask db init
    flask db migrate -m "Initial migration"
else
    echo "✅ Migrations directory found"
fi

echo "� Resetting migration history..."
# This ensures alembic_version matches our migration files
flask db stamp head 2>/dev/null || echo "⚠️ No existing migrations to stamp"

echo "�🚀 Applying database migrations..."
# Run migrations (will create/update tables)
flask db upgrade

echo "✅ Build completed successfully!"
