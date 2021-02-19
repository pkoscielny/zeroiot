
__version__ = "0.4.0"

from flask import Flask
from app.models import db
from app.resources import ResourceAirStateList, ResourceAirStateDetail, ResourceInsolationList, ResourceInsolationDetail
from app.config import config
from flask_rest_jsonapi import Api


def create_app(stage):
    if stage not in config.keys():
        stage = 'prod'

    app = Flask(__name__)
    app.config.from_object(config[stage])

    # Create db and all required tables if not exist.
    # It is important to run db.create_all() after load all models.
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Create an API.
    api = Api(app)
    api.route(ResourceAirStateList, 'air_state_list', '/air_state')
    api.route(ResourceAirStateDetail, 'air_state_detail', '/air_state/<int:id>')
    api.route(ResourceInsolationList, 'insolation_list', '/insolation')
    api.route(ResourceInsolationDetail, 'insolation_detail', '/insolation/<int:id>')

    return app
