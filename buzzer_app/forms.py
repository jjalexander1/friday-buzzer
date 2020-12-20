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
                                         render_kw={'class': 'form-control',  # specify this so that it renders the html element the same as the others
                                                    'id': 'timeEvaluationMethodInput',
                                                    'aria-describedby': 'timeEvaluationMethodHelp'},
                                         choices=['server', 'client', 'client_with_offset_correction', 'another'])
    one_buzz_per_question = SelectField("One Buzz Per Question",
                                         render_kw={'class': 'form-control',  # specify this so that it renders the html element the same as the others
                                                    'id': 'oneBuzzPerQuestionInput',
                                                    'aria-describedby': 'oneBuzzPerQuestionHelp'},
                                         choices=[('true', True), ('false', False)])  # explicit label/value in case it casts True to 'True'
    sort_latency = IntegerField("Sort Latency")