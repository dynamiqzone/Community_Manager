from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, admin_required

# created Flask instance
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Add database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# secret key
app.config["SECRET_KEY"] = "my super secret key that no one knows"

# initialize database
db = SQLAlchemy(app)


# Craeting class
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add_event")
@login_required
@admin_required  # Only admin can access this
def add_event():
    return render_template("add_event.html")


@app.route("/events")
@login_required
def events():
    # This is for Story 2.2: The Community Feed
    return render_template("events.html")


@app.route("/record_payment")
@login_required
@admin_required
def record_payment():
    return render_template("record_payment.html")


@app.route("/my_dues")
@login_required
def my_dues():
    return render_template("dues.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.hash, password):
            session["user"] = True
            session["first_name"] = user.first_name
            session["username"] = user.username
            session["role"] = user.role
            session["user_id"] = user.id
            return redirect("/")
        flash("Invalid username or password")
        return render_template("login.html")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()  # This removes 'user' and 'username' from the session
    return redirect("/login")


# Temporary route to preview ANY template
@app.route("/register", methods=["GET", "POST"])
def register():
    # Register user and add in db

    if request.method == "POST":
        user_name = request.form.get("username")
        f_name = request.form.get("first_name")
        l_name = request.form.get("last_name")
        passwords = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user_exists = Users.query.filter_by(username=user_name).first()
        existing_users_count = Users.query.count()
        user_role = "admin" if existing_users_count == 0 else "member"
        if user_exists:
            flash("Username is already taken. Try another!")
            return redirect("/register")
        if confirm_password != passwords:
            flash("Password do not match. Try again!")
            return redirect("/register")

        else:
            hashed_password = generate_password_hash(passwords)
            new_user = Users(
                username=user_name,
                first_name=f_name,
                last_name=l_name,
                hash=hashed_password,
                role=user_role,
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
