from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields


class SchemaAirState(Schema):
    class Meta:
        type_ = 'air_state'
        self_view = 'air_state_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'air_state_list'

    id = fields.Integer(as_string=True, dump_only=True)
    temperature = fields.Decimal(required=True)
    humidity = fields.Decimal(required=True)
    location = fields.Str(required=True)
    device = fields.Str(required=True)
    created = fields.DateTime(format="%Y-%m-%d %H:%M:%S")


class SchemaInsolation(Schema):
    class Meta:
        type_ = 'insolation'
        self_view = 'insolation_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'insolation_list'

    id = fields.Integer(as_string=True, dump_only=True)
    insolation = fields.Integer(required=True)
    device = fields.Str(required=True)
    created = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
