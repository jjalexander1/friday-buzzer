import datetime
import json
from typing import Dict, Any, Union

# Flask and Extensions
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_socketio import (
    SocketIO,
    emit,
    join_room,
    leave_room,
)

# Application-specific modules
from backend import RoomManager
from flask_app import app, forms, models, namespace, room_manager, socketio
from flask_app.forms import ParticipantNameForm, RoomSettingsForm
from flask_app.models import User


# --- Constants ---

# Removed LOCALHOST_URL_IDENTIFIERS and before_request as they were commented out
# and you explicitly removed the SSL configuration.

# --- Helper Functions ---

def send_message_to_room(payload: str, room_id: str) -> None:
    """Emits the room state update payload to all clients in a specific room."""
    emit('server_room_update', payload, room=room_id)


def broadcast_to_all_rooms(payload: str) -> None:
    """Emits the room state update payload to all connected clients."""
    emit('server_room_update', payload, broadcast=True)


def log_message_received(
        sent_from: str,
        room: str,
        event_name: str,
        sent_time: float = datetime.datetime.now().timestamp()
) -> None:
    """Logs incoming socket events to the console."""
    if isinstance(sent_time, float):
        sent_time = datetime.datetime.fromtimestamp(sent_time)

    print(
        f'{sent_time}, Room: {room} -- Player {sent_from} sent event {event_name}'
    )


# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def home():
    """Renders the main homepage."""
    return render_template("home.html")


@app.route('/music', methods=['GET', 'POST'])
@login_required
def redeemer():
    """Renders the music redeemer page (requires login)."""
    return render_template("redeemer.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    """Handles user logout."""
    logout_user()
    return redirect(url_for('home'))


@app.route('/buzzer', methods=['GET', 'POST'])
def buzzer_home():
    """Renders the buzzer system's entry page, handles room/name submission."""
    # busiest_rooms = room_manager.get_busiest_rooms() # commented out in original code
    form = ParticipantNameForm(request.form)

    if request.method == 'POST':
        # Assuming form submission goes through here to get name and room_id
        return redirect(url_for(
            "room",
            participant_name=form.participant_name.data,
            room_id=form.room_id.data
        ))

    # temporarily removed busiest_rooms=busiest_rooms from return
    return render_template("buzzer_home.html", form=form)


@app.route('/buzzer/room/<room_id>', methods=["GET", "POST"])
def room(room_id: str):
    """Renders the main buzzer room page and handles room setting updates."""
    room_id = room_id.upper()
    participant_name = request.args.get('participant_name')

    # Input Validation
    if not participant_name:
        return redirect(url_for("home"))
    if not participant_name.replace(" ", "").isalnum():
        raise Exception("Participant name provided contained disallowed characters")
    if not room_id.replace(" ", "").isalnum():
        raise Exception("Room name provided contained disallowed characters")

    form = RoomSettingsForm(request.form)

    # Check if a settings form submission occurred
    # The original logic relies on checking if *any* form data exists to trigger an update.
    if any(getattr(form, field).data is not None for field in
           ['correct_points', 'early_incorrect_points', 'sort_latency', 'time_evaluation_method',
            'one_buzz_per_question']):
        room = room_manager.get_room(room_id)
        config: Dict[str, Union[int, bool, str]] = {
            'correct_points': form.correct_points.data,
            'early_incorrect_points': form.early_incorrect_points.data,
            'sort_latency': form.sort_latency.data,
            'one_buzz_per_question': form.one_buzz_per_question.data,
            'time_evaluation_method': form.time_evaluation_method.data
        }
        room.update_config(config)

    return render_template("room.html", form=form, room_id=room_id, participant_name=participant_name)


@app.errorhandler(Exception)
def application_error(err):
    """Renders a custom error page for unhandled exceptions."""
    return render_template('error.html', error_type=str(type(err)), error=err)


# --- SocketIO Handlers ---

@socketio.on('buzz', namespace=namespace)
def handle_buzz(data: Dict[str, Any]) -> None:
    """Handles a player buzzing in."""
    server_side_time = datetime.datetime.now().timestamp()
    # Convert client time from milliseconds to seconds
    client_side_time = datetime.datetime.fromtimestamp(data['buzz_time'] / 1000).timestamp()

    room = room_manager.get_room(data['room_id'])
    room.buzz(
        data['participant_name'],
        client_side_time=client_side_time,
        server_side_time=server_side_time
    )

    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])

    log_message_received(
        sent_from=data['participant_name'],
        room=data['room_id'],
        event_name='buzz'
    )


@socketio.on('reset_buzzer', namespace=namespace)
def handle_buzzer_reset(data: Dict[str, Any]) -> None:
    """Handles the host resetting the buzzer."""
    room = room_manager.get_room(data['room_id'])
    room.reset_buzzer()

    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])

    log_message_received(
        sent_from=data['participant_name'],
        room=data['room_id'],
        event_name='reset_buzzer'
    )


@socketio.on('reset_room_scores', namespace=namespace)
def handle_scores_reset(data: Dict[str, Any]) -> None:
    """Handles the host resetting all player scores in a room."""
    room = room_manager.get_room(data['room_id'])
    room.reset_all_scores()

    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])

    log_message_received(
        sent_from=data['participant_name'],
        room=data['room_id'],
        event_name='reset_room_scores'
    )


@socketio.on('correct', namespace=namespace)
def handle_correct(data: Dict[str, Any]) -> None:
    """Handles the host marking the last buzz as correct."""
    room = room_manager.get_room(data['room_id'])
    room.mark_correct()

    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])

    log_message_received(
        sent_from=data['participant_name'],
        room=data['room_id'],
        event_name='correct'
    )


@socketio.on('standard_incorrect', namespace=namespace)
def handle_standard_incorrect(data: Dict[str, Any]) -> None:
    """Handles the host marking the last buzz as incorrect (standard)."""
    room = room_manager.get_room(data['room_id'])
    room.mark_standard_incorrect()

    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])

    log_message_received(
        sent_from=data['participant_name'],
        room=data['room_id'],
        event_name='standard_incorrect'
    )


@socketio.on('early_incorrect', namespace=namespace)
def handle_early_incorrect(data: Dict[str, Any]) -> None:
    """Handles the host marking the last buzz as incorrect (early/penalty)."""
    room = room_manager.get_room(data['room_id'])
    room.mark_early_incorrect()

    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=data['room_id'])

    log_message_received(
        sent_from=data['participant_name'],
        room=data['room_id'],
        event_name='early_incorrect'
    )


@socketio.on('join_room', namespace=namespace)
def handle_join_room(data: Dict[str, Any]) -> None:
    """Handles a client joining a room and broadcasting the initial state."""
    room_id = data['room_id']
    participant_name = data['participant_name']

    join_room(room_id, namespace=namespace)

    room_manager.add_room_if_not_exists(room_id)
    room = room_manager.get_room(room_id)
    room.add_player(participant_name)

    payload = room.get_room_state()
    send_message_to_room(payload=payload, room_id=room_id)

    log_message_received(
        sent_from=participant_name,
        room=room_id,
        event_name='join_room'
    )

    # Irving Saladino Easter egg logic
    if participant_name == "Irving Saladino":
        room_data = json.loads(payload)
        room_data["server_maintenance_alert"] = True
        maintenance_payload = json.dumps(room_data)
        broadcast_to_all_rooms(payload=maintenance_payload)


@socketio.on('leave_room', namespace=namespace)
def handle_leave_room(data: Dict[str, Any]) -> None:
    """Handles a client leaving a room."""
    leave_room(data['room_id'], namespace=namespace)

    log_message_received(
        sent_from=data['participant_name'],
        room=data['room_id'],
        event_name='leave_room'
    )


@socketio.on('my_ping', namespace=namespace)
def handle_ping(data: Dict[str, Any]) -> None:
    """Handles client-side pings for latency calculation."""
    server_side_time = datetime.datetime.now().timestamp()
    # Convert client time from milliseconds to seconds
    client_side_time = datetime.datetime.fromtimestamp(data['client_side_time'] / 1000).timestamp()

    room = room_manager.get_room(data['room_id'])
    player = room.get_player(data['participant_name'])

    # Calculate offset
    player.add_ping_offset(server_side_time - client_side_time)

    log_message_received(
        sent_from=data['participant_name'],
        room=data['room_id'],
        event_name='ping'
    )
