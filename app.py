"""Feedback Application."""

from flask import Flask, request, redirect, render_template, flash, get_flashed_messages, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterUserForm, LoginUserForm, FeedbackForm

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

        return redirect(f'/users/{user.username}')
    
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

            return redirect(f'/users/{user.username}')
        
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
    If user != logged in, redirect with flash messaging.
    """

    if "username" not in session:

        flash("You must be logged in to access that page!")

        return redirect('/')
    
    else:

        user = User.query.filter_by(username=username).first()

        details = user.get_details()

        username = details.get("Username")
        
        feedback_list = user.feedback

        return render_template('user.html', username=username, details = details, feedback_list=feedback_list)
    
@app.route('/users/<string:username>/delete', methods=["POST"])
def delete_user(username):
    """
    Delete the specified user.
    The user must be logged in and can only delete their own account.
    """

    if "username" not in session or session.get('username') != username:

        flash("You must be logged in to your own account to delete it.")

        return redirect('/')
    
    else:

        # user = User.query.filter_by(username=username).delete()

        # the line above to get user led to some kind of integrity error which im still confused about but the below seems to work
        user = User.query.get(username)
        db.session.delete(user)

        db.session.commit()

        session.pop("username")

        # how do i cascade the deletion so that deleting the user also deletes all of the feedback from them?

        return redirect('/')
    
@app.route('/users/<string:username>/feedback/add', methods=["GET", "POST"])
def handle_new_feedback(username):
    """
    GET: Show a form that adds new feedback when submitted.
    POST: Handle submission of new feedback and redirect to '/users/<username>'
    User must be logged in to view and submit feedback form.
    """

    if "username" not in session or session.get('username') != username:

        # flash(f"{'username' not in session}")
        # flash(f"{session.get('username')}")
        # flash(f"{username}")

        flash("You must be logged in as that user to add feedback.")

        return redirect('/')

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()

        flash(f"Feedback '{feedback.title}' from {feedback.username} submitted!")

        return redirect(f'/users/{username}')
    
    else:
        return render_template('feedback.html', form=form)
    
@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def handle_update_feedback(feedback_id):
    """
    GET: Show a form to edit the specified feedback.
    POST: Handle submission of edits to specified feedback and redirect to '/users/<username>'
    User must be logged in as the author of the feedback to edit.
    """

    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or session.get('username') != feedback.username:

        # flash(f"{session.get('username')} COMPARED TO {feedback.username}")

        flash("You must be logged in as the author of the feedback to edit it.")

        return redirect('/')

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        flash(f"Feedback updated!")

        return redirect(f'/users/{feedback.username}')
    
    else:
        return render_template('feedback.html', form=form)
    
@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def handle_delete_feedback(feedback_id):
    """
    Handle deletion of a specified feedback.
    User must be logged in as the author of the feedback to delete.
    Redirects to '/users/<username>'
    """

    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or session.get('username') != feedback.username:

        flash("You must be logged in as the author of the feedback to delete it.")

        return redirect('/')
    
    else:

        db.session.delete(feedback)
        db.session.commit()

        return redirect(f'/users/{feedback.username}')
    




