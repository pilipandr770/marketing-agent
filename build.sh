#!/usr/bin/env bash
# exit on error
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

echo "🚀 Applying database migrations..."
# Run migrations (will create/update tables)
flask db upgrade

echo "✅ Build completed successfully!"
