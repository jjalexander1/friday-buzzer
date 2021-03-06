import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = True  # Turns on debugging features in Flask
    SECRET_KEY = b"'\x8d\x0f\xda\xf3\xaeC \xfe\x89\x1a\xc5\x88\xf0\xf7?\xdcqT\x9a\x8f),z\xc6O\x9e\x03\xa9uW\x8b"
    SOCKETIO_ASYNC_MODE="eventlet"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False