from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    goal = StringField('Goal', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    desired_password = StringField('Desired Password', validators=[DataRequired(), Length(min=6, max=30)])
    submit = SubmitField('Reset Password')



class PlanForm(FlaskForm):
    plan_name = StringField('Plan Name', validators=[DataRequired()])
    plan_type = StringField('Plan Type')
    plan_duration = StringField('Plan Duration')
    submit = SubmitField('Create Plan')