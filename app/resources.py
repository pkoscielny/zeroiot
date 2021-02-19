from flask_rest_jsonapi import ResourceList, ResourceDetail
from app.models import ModelAirState, ModelInsolation, db
from app.schemas import SchemaAirState, SchemaInsolation


class ResourceAirStateList(ResourceList):
    schema = SchemaAirState
    data_layer = {'session': db.session, 'model': ModelAirState}


class ResourceAirStateDetail(ResourceDetail):
    schema = SchemaAirState
    data_layer = {'session': db.session, 'model': ModelAirState}


class ResourceInsolationList(ResourceList):
    schema = SchemaInsolation
    data_layer = {'session': db.session, 'model': ModelInsolation}


class ResourceInsolationDetail(ResourceDetail):
    schema = SchemaInsolation
    data_layer = {'session': db.session, 'model': ModelInsolation}
