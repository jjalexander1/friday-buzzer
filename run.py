from views import app, socketio

import eventlet

eventlet.monkey_patch()
# from gevent import monkey
#
# monkey.patch_all()

socketio.init_app(app)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
