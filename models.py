"""Models for Flask Feedback application."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    with app.app_context():

        db.app = app
        db.init_app(app)

class User(db.Model):
    """A user."""

    __tablename__ = "users"

    username = db.Column(db.String(20),
                         primary_key=True) # iirc primary key implies uniqueness
    
    password = db.Column(db.Text,
                         nullable=False)
    
    email = db.Column(db.String(50),
                      nullable=False,
                      unique=True)
    
    first_name = db.Column(db.String(30),
                           nullable=False)
    
    last_name = db.Column(db.String(30),
                          nullable=False)
    
    def get_details(self):
        """
        Returns a dictionary with information about the user.
        Excludes password.
        """
        return {
            "Username": self.username,
            "Email" : self.email,
            "First Name": self.first_name,
            "Last Name": self.last_name
        }
    
    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """
        Register a user with the provided username, email, first & last name, 
        and a hashed password. Returns user.
        """

        hashed_password = bcrypt.generate_password_hash(password)

        hashed_password_utf8 = hashed_password.decode("utf8")

        return cls(username=username, password=hashed_password_utf8, email=email, first_name=first_name, last_name=last_name)
    
    @classmethod
    def authenticate(cls, username, password):
        """
        Validate that username exists and the provided password is correct for that user.
        Returns the user if valid. Otherwise, returns False.
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
    
