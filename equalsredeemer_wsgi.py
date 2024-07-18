
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/equalsredeemer/'
if project_home not in sys.path:
    sys.path.append(project_home)

# Tell Flask to use the production configuration
os.environ['FLASK_ENV'] = 'production'

from app import app, socketio


socketio.init_app(app)

# Example of handling Socket.IO events (you should define your own handlers)
@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

# For production, the Flask-SocketIO server should be run using Socket.IO's WSGI support
if __name__ == '__main__':
    socketio.run(app)
