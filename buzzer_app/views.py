import time
import re
import json

from flask import request, redirect, url_for, render_template, Flask
from flask_socketio import emit, join_room, leave_room, SocketIO
from threading import Thread


from buzzer_app.backend import RoomManager, Player
from buzzer_app.forms import ParticipantNameForm, RoomSettingsForm

# TODO make ping frequency an application configuration

import datetime
app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(async_mode="eventlet")
namespace = '/friday_buzzer'
thread = None
room_manager = RoomManager()

LOCALHOST_URL_IDENTIFIERS = ['//localhost',
                             '//127.0.0.1',
                             '//0.0.0.0']

# def background_thread():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         time.sleep(10)
#         count += 1
#         socketio.emit('my response',
#                       {'data': 'Server generated event', 'count': count},
#                       namespace='/test')


@app.before_request
def before_request():  # force to use https
    for l in LOCALHOST_URL_IDENTIFIERS:
        if l in request.url:
            if request.url.startswith('https://'):
                url = request.url.replace('https://', 'http://', 1)  # flask doesn't like https requests on localhost
                code = 301
                return redirect(url, code=code)
            return
    if request.url.startswith('http://'):  # otherwise always use https
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


@app.route('/', methods=['GET', 'POST'])
def home():
    print('hi')
    global room_manager
    busiest_rooms = room_manager.get_busiest_rooms()

    # global thread
    # if thread is None:
    #     thread = Thread(target=background_thread)
    #     thread.daemon = True
    #     thread.start()

    form = ParticipantNameForm(request.form)
    if request.method == 'POST':
        return redirect(url_for("room", participant_name=form.participant_name.data, room_id=form.room_id.data))
    return render_template("home.html", form=form, busiest_rooms=busiest_rooms)


@app.route('/room/<room_id>', methods=["GET", "POST"])
def room(room_id):
    room_id = room_id.lower()  # make case insensitive
    participant_name = request.args.get('participant_name')
    global BAD_CHARS
    if not participant_name:  # force players to go through the homepage, don't bother erroring
        return redirect(url_for("home"))
    if not participant_name.replace(" ", "").isalnum():
        raise Exception("Participant name provided contained disallowed characters")
    if not room_id.replace(" ", "").isalnum():
        raise Exception("Room name provided contained disallowed characters")

    form = RoomSettingsForm(request.form)
    if form.correct_points.data is not None or form.early_incorrect_points.data is not None or form.sort_latency.data is not None or form.time_evaluation_method.data is not None or form.one_buzz_per_question.data is not None:
        global room_manager
        room = room_manager.get_room(room_id)
        config = dict(correct_points=form.correct_points.data,
                      early_incorrect_points=form.early_incorrect_points.data,
                      sort_latency=form.sort_latency.data,
                      one_buzz_per_question=form.one_buzz_per_question.data,
                      time_evaluation_method=form.time_evaluation_method.data)
        room.update_config(config)
    return render_template("room.html", form=form, room_id=room_id, participant_name=participant_name)


@app.errorhandler(Exception)
def application_error(err):
    return render_template('error.html', error_type=str(type(err)), error=err)


@socketio.on('buzz', namespace=namespace)
def handle_buzz(data):
    server_side_time = datetime.datetime.now().timestamp()
    client_side_time = datetime.datetime.fromtimestamp(data['buzz_time'] / 1000).timestamp()  # convert from ms to s
    global room_manager
    room = room_manager.get_room(data['room_id'])
    room.buzz(data['participant_name'], client_side_time=client_side_time, server_side_time=server_side_time)
    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])
    log_message_received(sent_from=data['participant_name'],
                         room=data['room_id'],
                         event_name='buzz')


@socketio.on('reset_buzzer', namespace=namespace)
def handle_buzzer_reset(data):
    global room_manager
    room = room_manager.get_room(data['room_id'])
    room.reset_buzzer()
    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])
    log_message_received(sent_from=data['participant_name'],
                         room=data['room_id'],
                         event_name='reset_buzzer')


@socketio.on('reset_room_scores', namespace=namespace)
def handle_scores_reset(data):
    global room_manager
    #room_manager.cleanup_rooms()  # for now don't do any room cleanup, just store all historic data
    room = room_manager.get_room(data['room_id'])
    room.reset_all_scores()
    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])
    log_message_received(sent_from=data['participant_name'],
                         room=data['room_id'],
                         event_name='reset_room_scores')


@socketio.on('correct', namespace=namespace)
def handle_correct(data):
    global room_manager
    room = room_manager.get_room(data['room_id'])
    room.mark_correct()
    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])
    log_message_received(sent_from=data['participant_name'],
                         room=data['room_id'],
                         event_name='correct')


@socketio.on('standard_incorrect', namespace=namespace)
def handle_standard_incorrect(data):
    global room_manager
    room = room_manager.get_room(data['room_id'])
    room.mark_standard_incorrect()
    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])
    log_message_received(sent_from=data['participant_name'],
                         room=data['room_id'],
                         event_name='standard_incorrect')


@socketio.on('early_incorrect', namespace=namespace)
def handle_early_incorrect(data):
    global room_manager
    room = room_manager.get_room(data['room_id'])
    room.mark_early_incorrect()
    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])
    log_message_received(sent_from=data['participant_name'],
                         room=data['room_id'],
                         event_name='early_incorrect')


@socketio.on('join_room', namespace=namespace)
def handle_join_room(data):
    join_room(data['room_id'], namespace=namespace)

    global room_manager
    room_manager.add_room_if_not_exists(data['room_id'])
    new_room = room_manager.get_room(data['room_id'])
    new_room.add_player(data['participant_name'])
    payload = new_room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])
    log_message_received(sent_from=data['participant_name'],
                         room=data['room_id'],
                         event_name='join_room')


@socketio.on('leave_room', namespace=namespace)
def handle_leave_room(data):
    leave_room(data['room_id'], namespace=namespace)
    log_message_received(sent_from=data['participant_name'],
                         room=data['room_id'],
                         event_name='leave_room')
    # don't yet remove the player from the room..


@socketio.on('my_ping', namespace=namespace)
def handle_ping(data):
    server_side_time = datetime.datetime.now().timestamp()
    client_side_time = datetime.datetime.fromtimestamp(data['client_side_time'] / 1000).timestamp()  # convert from ms to s
    log_message_received(sent_from=data['participant_name'],
                         room=data['room_id'],
                         event_name='ping')

    global room_manager
    room = room_manager.get_room(data['room_id'])
    player = room.get_player(data['participant_name'])
    player.add_ping_offset(server_side_time - client_side_time)


def send_message_to_room(payload, room_id):  # wrap a room broadcast message
    emit('server_room_update', payload, room=room_id)


def log_message_received(sent_from, room, event_name, sent_time=datetime.datetime.now().timestamp()):
    if isinstance(sent_time, float):
        sent_time = datetime.datetime.fromtimestamp(sent_time)
    print('{sent_time}, Room: {room} -- Player {sent_from} sent event {event_name}'.format(sent_time=sent_time,
                                                                                           room=room,
                                                                                           sent_from=sent_from,
                                                                                           event_name=event_name))
