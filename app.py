import os
from flask import Flask, render_template, redirect, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import Session

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
# Keep this secret! No oopsie-whoopsies!
# Do NOT use this in a production enviroment. Follow the flask documentation to generate you own,
# and ideally use environment variables
app.config["SECRET_KEY"] = "fb7f067a03c408275de2f89e991b3d97548553ee17cec8c8deb1f64a7c6ec34d"

# Get them logins inited
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)

class Members(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey("families.id"), nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=False)

class Families(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    members = db.relationship("Members", backref="family", lazy=True)

with app.app_context():
    db.create_all()
    print("Database created successfully.")


# User loader thingy for flask-login
@login_manager.user_loader
def load_user(id):
    return db.session.get(User, id)

# Signup route that stores creds in db (password is hashed)
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Get all fields
        username = request.form.get("username")
        password = request.form.get("password")
        again = request.form.get("again")

        if password != again:
            flash("Passwords do not match")

        # Check if the user exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect("/signup")

        # Create a variable to store the new users creds
        new_user = User(username=username, password_hash=generate_password_hash(password, method="pbkdf2:sha256"))

        # Modify the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the login page
        return redirect("/login")

    return render_template("signup.html")

# Login route that uses flask-login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get data from the form
        username = request.form.get("username")
        password = request.form.get("password")
        again = request.form.get("again")
        remember = request.form.get("remember")

        if again != password:
            flash("Passwords do not match")
            return redirect("/login")

        # Check if the user actually exists
        user = User.query.filter_by(username=username).first()

        # Take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password_hash, password):
            flash("Please check your login details and try again.")
            return redirect("/login") # if the user doesn't exist or password is wrong, reload the page

        # If the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember is not None)
        return redirect("/")
    return render_template("login.html")

# Logs out users
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# Index route that lists members and checks them in
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":

        name = request.form.get("name")
        family_name = request.form.get("family_name")

        if not name or not family_name:
            flash("Please enter both Name and Family name.")
            return redirect("/")
        name = name.title()
        family = Families.query.filter_by(name=family_name.title()).first()
        if family:
            new_member = Members(name=name, family=family)
            db.session.add(new_member)
            db.session.commit()
        else:
            flash(f"Family \"{family_name}\" not found.")

        return redirect("/")

    if q := request.args.get("q"):
        stmt = select(Members, Families).join(Families, Members.family_id == Families.id).filter(Members.name.like(q.title())) #Join Members and Families
        results = db.session.execute(stmt).all() #Fetch results as tuples
        result = [{
            "id": member.id,
            "name": member.name,
            "family_id": member.family_id,
            "status": member.status,
            "family_name": family.name
        } for member, family in results]

        return render_template("index.html", rows=result)


    elif member_id := request.args.get("id"):

        print(member_id)

        member = Members.query.filter_by(id=member_id).first()
        member.status = not member.status  # Toggle the boolean value
        db.session.commit()

        return redirect("/")

    elif member_id := request.args.get("del_id"):
        print(member_id)
        member = db.session.get(Members, member_id)  # More efficient way to get by ID
        print(member)
        db.session.delete(member)
        db.session.commit()
        return redirect("/")



    stmt = select(Members, Families).join(Families, Members.family_id == Families.id) #Join Members and Families
    results = db.session.execute(stmt).all() #Fetch results as tuples
    result = [{
        "id": member.id,
        "name": member.name,
        "family_id": member.family_id,
        "status": member.status,
        "family_name": family.name
    } for member, family in results]

    return render_template("index.html", rows=result)

@app.route("/families", methods=["GET", "POST"])
@login_required
def families():
    if request.method == "POST":

        name = request.form.get("name")

        if not name:
            flash("Please enter Family Name")

        new_family = Families(name=name)
        db.session.add(new_family)
        db.session.commit()

        return redirect("/families")

    if q := request.args.get("q"):

        all_families = db.session.query(Families).filter(Families.name.like(q))
        result = [{
            "id": family.id,
            "name": family.name,
        } for family in all_families]

        return render_template("families.html", rows=result)

    elif family_id := request.args.get("id"):
        print(family_id)
        family = db.session.get(Families, family_id)
        members = db.session.query(Members).filter_by(family_id=family_id).all()
        if members:
            flash(f"{len(members)} member(s) is(are) using this family. Delete them first.")
            return redirect("/families")
        print(family)
        db.session.delete(family)
        db.session.commit()
        return redirect("/families")

    all_families = db.session.query(Families).all()
    result = [{
        "id": family.id,
        "name": family.name,
    } for family in all_families]

    return render_template("families.html", rows=result)

@app.route("/check", methods=["POST"])
@login_required
def check():
    member_id = request.form.get("id")

    print(member_id)

    member = Members.query.filter_by(id=member_id).first()
    member.status = not member.status  # Toggle the boolean value
    db.session.commit()

    return redirect("/")


@app.route("/user", methods=["GET", "POST"])
@login_required
def user():
    if request.method == "POST":

        if delpass := request.form.get("delpass"):
            user = db.session.get(User, current_user.id)
            if check_password_hash(user.password_hash, delpass):
                db.session.delete(user)
                db.session.commit()
                return redirect("/")
            else:
                flash("Password incorrect")
                return redirect("/user")
        else:
            flash("Please enter password")
            return redirect("/user")
        oldpass = request.form.get("oldpass")
        newpass = request.form.get("newpass")
        again = request.form.get("again")

        if not oldpass or not newpass or not again:
            flash("Please fill in all fields.")
            return redirect("/user")

        if newpass != again:
            flash("New passwords do not match.")
            return redirect("/user")

        user = User.query.filter_by(id=current_user.id).first()
        if user:
            if check_password_hash(user.password_hash, oldpass):
                user.password_hash = generate_password_hash(newpass, method="pbkdf2:sha256")
                db.session.commit()
                flash("Password changed successfully!")
                return redirect("/")
            else:
                flash("Incorrect old password.")
                return redirect("/user")
        else:
            flash("User not found.")  #Handle missing user
            return redirect("/user") #Return to prevent errors after flash message

    return render_template("user.html")

if __name__ == "__main__":
    app.run(debug=True)
