from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Register the main Blueprint
    from app.main.routes import main
    app.register_blueprint(main)

    return app
