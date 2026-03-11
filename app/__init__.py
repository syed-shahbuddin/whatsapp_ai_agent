from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint


def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)

    return app
