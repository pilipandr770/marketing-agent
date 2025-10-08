# file: run.py
from app import create_app, db

app = create_app()

# Ensure database tables exist on startup (for production)
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables verified/created successfully!")
    except Exception as e:
        print(f"⚠️ Error with database tables: {e}")

if __name__ == "__main__":
    # For development - use flask run in production
    app.run(host="0.0.0.0", port=5000, debug=True)