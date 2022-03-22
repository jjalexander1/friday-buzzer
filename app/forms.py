from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ParticipantNameForm(FlaskForm):
    participant_name = StringField("Participant Name")
    room_id = StringField("Room")


class RoomSettingsForm(FlaskForm):
    participant_name = StringField("Participant Name")
    room_id = StringField("Room")
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
