from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    #Database connection
    db.init_app(app)

    # Register the main Blueprint
    from app.main.routes import main
    app.register_blueprint(main)

    return app
