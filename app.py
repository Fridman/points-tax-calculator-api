import logging

from flask import Flask
from logging.handlers import TimedRotatingFileHandler

from api import calculate_tax_bp
from api.exceptions import exceptions_bp

from common.extensions import cache

prod_config = {
    "DEBUG": False,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    "TAX_API_SERVER_URL": "http://localhost:5001", # Change for deployment
}

test_config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    "TAX_API_SERVER_URL": "http://localhost:5001",
}


def create_app():

    app = Flask(__name__)

    config = prod_config
    if app.debug == True:
        config = test_config

    _register_blueprints(app)
    file_handler = TimedRotatingFileHandler(
        'logs/tax_calculator.log',
        when='midnight',
        backupCount=1,
    )
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.config.from_mapping(config)
    app.logger.setLevel(logging.ERROR)

    cache.init_app(app, config=config)

    return app


def _register_blueprints(app):
    app.register_blueprint(calculate_tax_bp)
    app.register_blueprint(exceptions_bp)
