from app import app
from extensions import db

# Create the database and tables within the app context
with app.app_context():
    db.create_all()
    print("Database tables created successfully.")
