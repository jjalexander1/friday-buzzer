from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from backend import RoomManager
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(async_mode="eventlet")
namespace = '/friday_buzzer'
thread = None
room_manager = RoomManager()
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models
