
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/equalsredeemer/'
if project_home not in sys.path:
    sys.path.append(project_home)

# Tell Flask to use the production configuration
os.environ['FLASK_ENV'] = 'production'

from flask_app import app




# For production, the Flask-SocketIO server should be run using Socket.IO's WSGI support
if __name__ == '__main__':
    socketio.run(app)
