from flask_wtf import FlaskForm
from wtforms.fields import StringField, IntegerField, SelectField


class ParticipantNameForm(FlaskForm):
    participant_name = StringField("Participant Name")
    room_id = StringField("Room ID")


class RoomSettingsForm(FlaskForm):
    participant_name = StringField("Participant Name")
    room_id = StringField("Room ID")
    correct_points = IntegerField("Correct Points")
    early_incorrect_points = IntegerField("Early Incorrect Points")
    time_evaluation_method = SelectField("Early Incorrect Points",
                                         render_kw={'class': 'form-control',
                                                    'id': 'timeEvaluationMethodInput',
                                                    'aria-describedby': 'timeEvaluationMethodHelp'},
                                         choices=['server', 'client', 'client_with_offset_correction', 'another'])
    sort_latency = IntegerField("Sort Latency")
