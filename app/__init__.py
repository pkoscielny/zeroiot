"""
TODO:
* sprobowac zrobic bardziej zaawansowana wersje listy, z filtrami, sortem, etc.
* dodac wersje kodu
* dodac unit testy
* dodac "POD"
* ? pip3 freeze > requirements.txt
"""

# PyCharm:
# FLASK_APP=app:create_app('dev') FLASK_ENV=development python -m flask run --port=3000

# Flask uses simplejson (or json from stdlib if not found) but flask_restful uses json from stdlib always.
# It is because simplejson contains some extra things which are not in JSON standard.
# Also Flask uses jsonify e.g. for sorting keys (better cooperation with HTTP caches).
# I don't need caching this content so I decided to leave it as simple as possible (jsonification by flask_restful).
# Consider using jsonify if e.g. I need jsonify more complex structures:
#  https://flask.palletsprojects.com/en/1.1.x/api/#module-flask.json

from flask import Flask
from flask_restful import Api
from app.models import db
from app.resources import ResourceAirState, ResourceInsolation
from app.config import config


# Flask will automatically detect the factory (create_app or make_app) in this app.
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
    api.add_resource(ResourceAirState, '/air_state')
    api.add_resource(ResourceInsolation, '/insolation')

    return app
