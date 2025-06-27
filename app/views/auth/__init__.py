from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, Regexp
from app.extensions import db
from app.models.user import User
from typing import Optional as TypingOptional, Union, cast
from werkzeug.wrappers import Response


auth_bp = Blueprint('auth', __name__, template_folder='../../templates/auth')

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Regexp(r'^\+?1?\d{9,15}$', message="Invalid phone number")])
    whatsapp = StringField('WhatsApp', validators=[Optional(), Regexp(r'^\+?1?\d{9,15}$', message="Invalid WhatsApp number")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Account Type', choices=[('user', 'General User'), ('farmer', 'Farmer')], default='user', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username: StringField) -> None:
        user: TypingOptional[User] = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email: StringField) -> None:
        user: TypingOptional[User] = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=cast(str, form.username.data),
            email=cast(str, form.email.data),
            password=cast(str, form.password.data),
            phone=form.phone.data,
            whatsapp=form.whatsapp.data,
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login() -> Union[str, Response]:
    form = LoginForm()
    if form.validate_on_submit():
        user: TypingOptional[User] = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(cast(str, form.password.data)):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            if user.role == 'farmer':
                return redirect(url_for('farmer.dashboard'))
            return redirect(url_for('main.index'))
        flash('Invalid email or password.', 'error')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout() -> Response:
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
