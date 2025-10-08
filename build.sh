#!/usr/bin/env bash
# eecho "🚀 Applying database migrations..."
# Run migrations (will create/update tables)
flask db upgrade

echo "🔧 Applying manual migration for LinkedIn and Meta fields..."
# Apply manual SQL migration (idempotent - safe to run multiple times)
if [ -f "manual_migration.sql" ]; then
    python -c "
import os
import psycopg
from urllib.parse import urlparse

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL')
if db_url:
    # Read SQL file
    with open('manual_migration.sql', 'r') as f:
        sql = f.read()
    
    # Execute SQL
    try:
        conn = psycopg.connect(db_url)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
        print('✅ Manual migration applied successfully')
    except Exception as e:
        print(f'⚠️ Manual migration warning: {e}')
else:
    print('⚠️ DATABASE_URL not set, skipping manual migration')
"
fi

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
