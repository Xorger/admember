import os
from flask.templating import _render
from typing_extensions import NewType
from flask import Flask, render_template, redirect, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
import flask_login
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
# Keep this secret! No oopsie-whoopsies!
app.config["SECRET_KEY"] = "fb7f067a03c408275de2f89e991b3d97548553ee17cec8c8deb1f64a7c6ec34d"

# Get them logins inited
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    name = db.Column(db.String(100), nullable = False)
    password_hash = db.Column(db.String(80), nullable = False)

class Members(db.Model):
    member_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), nullable = False)


with app.app_context():
    db.create_all()
    print("Database created successfully.")


# User loader thingy for flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Signup route that stores creds in db (password is hashed)
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Get all fields
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")

        print(f"Received: username={username}, name={name}")

        # Check if the user exists
        if User.query.filter_by(username=username).first():
            return redirect("/signup")

        # Create a variable to store the new users creds
        new_user = User(username=username, name=name, password_hash=generate_password_hash(password, method="pbkdf2:sha256"))

        # Modify the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the login page
        return redirect("/login")

    return render_template("signup.html")

# Login route that uses flask-login
@app.route("/login", methods=["GET", "POST"])
def login():
    return "Login Page (TODO)"

# Index route that lists members and checks them in
@app.route("/")
def index():
    return "Index (TODO)"
    #return render_template("index.html", rows=None)

if __name__ == "__main__":
    app.run(debug=True)
