# file: run.py
from app import create_app

app = create_app()

# Note: Database migrations are handled by Flask-Migrate during build process
# See build.sh for migration commands (flask db upgrade)
# DO NOT use db.create_all() in production - it bypasses migrations!

if __name__ == "__main__":
    # For development - use flask run in production
    app.run(host="0.0.0.0", port=5000, debug=True)