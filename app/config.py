from configparser import ConfigParser

config = ConfigParser()
config.read('configs/config.ini')
sqlite_db = config['DATABASE']['SQLITE_DB']


class BaseConfig:
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///../{sqlite_db}'


class DevelopmentConfig(BaseConfig):
    pass
    # SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    DEBUG = False


config = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig,
)
