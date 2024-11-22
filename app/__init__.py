from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db = SQLAlchemy(app)

# Import routes and models
from app import routes, models

# Create the database and the tables
with app.app_context():
    db.create_all()
