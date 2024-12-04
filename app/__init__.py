from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize the login manager
login = LoginManager(app)
login.login_view = 'login'

# Register Blueprints
from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

# Import routes and models
from app import routes, models
