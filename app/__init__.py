import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy globally
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Load configuration settings
    app.config.from_object('config.Config')
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'submissions')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Initialize the database connection
    db.init_app(app)

    # Import and register blueprints
    from app.main import main
    from app.admin import admin
    from app.professor import professor
    from app.student import student
    
    app.register_blueprint(main, url_prefix='/') 
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(professor, url_prefix='/professor') 
    app.register_blueprint(student, url_prefix='/student') 
      
    return app
