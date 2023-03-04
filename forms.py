"""WTForms for Feedback Application."""

from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import InputRequired

class RegisterUserForm(FlaskForm):
    """Form for registering a new user to the application database."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])

class LoginUserForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    """Form for creating or updating feedback."""

    title = StringField('Title', validators=[InputRequired()])
    content = StringField('Content', validators=[InputRequired()])