from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from backend import RoomManager
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# --- START: SOCKETIO CONFIGURATION UPDATE ---
socketio = SocketIO(
    async_mode="eventlet",
    cors_allowed_origins='*',
    # CRITICAL FIX: Explicitly allow the old EIO=3 protocol
    engineio_options={'ping_interval': 5, 'ping_timeout': 30, 'json': None}
)
# --- END: SOCKETIO CONFIGURATION UPDATE ---

# REMOVED: namespace = '/friday_buzzer'
namespace = None  # Retain a placeholder to avoid breaking 'from flask_app import namespace' if other files use it

thread = None
room_manager = RoomManager()
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

socketio.init_app(app)
from flask_app import views, models