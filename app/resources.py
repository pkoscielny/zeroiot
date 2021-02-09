from flask_restful import Resource, reqparse
from app.models import ModelAirState, ModelInsolation, db


# Request parser configuration for params validation.
# I don't want to put this parser as class attribute because I want avoid not needed many instances of the same parser.
# So it should be a singleton.
parser_air_state = reqparse.RequestParser(trim=True, bundle_errors=True)
parser_air_state.add_argument('temperature', type=float, required=True, help="temperature is required parameter!")
parser_air_state.add_argument('humidity', type=float, required=True, help="humidity is required parameter!")
parser_air_state.add_argument('location', type=str, required=True, help="location is required parameter!")
parser_air_state.add_argument('device', type=str, required=True, help="device is required parameter!")
class ResourceAirState(Resource):

    def get(self):
        rows = ModelAirState.query.all()
        return [ModelAirState.serialize(row) for row in rows]

    def post(self):
        args = parser_air_state.parse_args()
        row = ModelAirState(
            temperature = args['temperature'],
            humidity    = args['humidity'],
            location    = args['location'],
            device      = args['device'],
        )
        db.session.add(row)
        db.session.commit()

        return ModelAirState.serialize(row), 201


parser_insolation = reqparse.RequestParser(trim=True, bundle_errors=True)
parser_insolation.add_argument('insolation', type=int, required=True, help="insolation is required parameter!")
parser_insolation.add_argument('device', type=str, required=True, help="device is required parameter!")
class ResourceInsolation(Resource):

    def get(self):
        rows = ModelInsolation.query.all()
        # rows = ModelInsolation.query.filter(ModelInsolation.id > 5)
        return [ModelInsolation.serialize(row) for row in rows]

    def post(self):
        args = parser_insolation.parse_args()
        row = ModelInsolation(
            insolation = args['insolation'],
            device     = args['device']
        )
        db.session.add(row)
        db.session.commit()

        return ModelInsolation.serialize(row), 201
