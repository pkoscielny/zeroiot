from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AuditMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ModelAirState(db.Model, AuditMixin):
    __tablename__ = 'air_states'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    temperature = db.Column(db.Float, nullable=False, comment="In Celsius degrees")
    humidity = db.Column(db.Float, nullable=False, comment="The relative humidity in %")
    location = db.Column(db.String, nullable=False, comment="The name of the location, e.g. kitchen")
    device = db.Column(db.String, nullable=False, comment="Device ID where sensor is connected")

    def serialize(self):
        return {
            'id': self.id,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'location': self.location,
            'device': self.device,
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S"),
        }


class ModelInsolation(db.Model, AuditMixin):
    __tablename__ = 'insolations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    insolation = db.Column(db.Integer, nullable=False, comment="The insolation value from sensor")
    device = db.Column(db.String, nullable=False, comment="Device ID where sensor is connected")

    def serialize(self):
        return {
            'id': self.id,
            'insolation': self.insolation,
            'device': self.device,
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S"),
        }
