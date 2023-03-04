"""Feedback Application."""

from flask import Flask, request, redirect, render_template, flash, get_flashed_messages, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterUserForm, LoginUserForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "my_feedback"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)
# with app.app_context(): drama

@app.route('/')
def redirect_to_register():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def handle_registration():
    """
    GET: Show a form that creates a user when submitted.
    POST: Process submission and create user. Redirects to '/secret'
    """

    form = RegisterUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data 
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)

        db.session.add(user)
        db.session.commit()

        flash(f"Registered {first_name} {last_name} at {email} with username {username}. Welcome!")

        session['username'] = user.username

        return redirect('/secret')
    
    else:
        return render_template('register.html', form=form)
    
@app.route('/login', methods=["GET", "POST"])
def handle_login():
    """
    GET: Show a form to log in a user when submitted.
    POST: Process login, ensure user authentication, and redirect to '/secret' if successful.
    """

    form = LoginUserForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:

            session['username'] = user.username

            return redirect('/secret')
        
        else:
            form.username.errors = ["Incorrect username or password."]

    return render_template('login.html', form=form)

@app.route('/secret')
def show_secret():
    """
    Show registered, logged-in users the secret text.
    """

    if "username" not in session:

        flash("You must be logged in to access that page!")

        return redirect('/')
    
    else:
        return render_template('secret.html')
    
@app.route('/logout')
def log_user_out():
    """Logs user out and redirects to registration page."""

    session.pop("username")

    return redirect('/')

@app.route('/users/<string:username>') # might be str not string
def show_user_information(username):
    """
    Show information about the current user.
    If user is not logged in, redirect with flash messaging.
    """

    if "username" not in session:

        flash("You must be logged in to access that page!")

        return redirect('/')
    
    else:

        user = User.query.filter_by(username=username).first()

        details = user.get_details()

        return render_template('user.html', details = details)