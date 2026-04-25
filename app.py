from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, admin_required
from sqlalchemy import func

# Created Flask instance
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Add database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# Secret key
app.config["SECRET_KEY"] = "my super secret key that no one knows"

# Initialize database
db = SQLAlchemy(app)

# --- MODELS ---


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")
    is_founder = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.String(10), nullable=False)
    event_time = db.Column(db.String(5), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(200), nullable=False)
    date_paid = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("Users", backref=db.backref("payments", lazy=True))


class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    status = db.Column(db.String(20), default="accepted")  # accepted, pending
    is_volunteer = db.Column(db.Boolean, default=False)
    volunteer_role = db.Column(
        db.String(100), nullable=True
    )  # "Catering", "Chairs", etc.
    __table_args__ = (db.UniqueConstraint("user_id", "event_id", name="unique_rsvp"),)

    # Add these relationships to make the HTML cleaner
    user = db.relationship("Users", backref=db.backref("rsvps", lazy=True))
    event = db.relationship("Events", backref=db.backref("rsvps", lazy=True))


class Announcements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(
        db.Boolean, default=True
    )  # Allows hiding the bar without deleting


with app.app_context():
    db.create_all()

# --- ROUTES ---


@app.route("/")
def index():
    events = Events.query.all()
    counts_query = (
        db.session.query(RSVP.event_id, func.count(RSVP.id))
        .group_by(RSVP.event_id)
        .all()
    )
    attendance_counts = {item[0]: item[1] for item in counts_query}

    user_total_paid = 0
    user_rsvps = []
    announcement = (
        Announcements.query.filter_by(is_active=True)
        .order_by(Announcements.date_posted.desc())
        .first()
    )
    if session.get("user_id"):
        user_total_paid = (
            db.session.query(func.sum(Transactions.amount))
            .filter_by(user_id=session["user_id"])
            .scalar()
            or 0
        )
        user_rsvps = [
            r.event_id for r in RSVP.query.filter_by(user_id=session["user_id"]).all()
        ]

    return render_template(
        "index.html",
        events=events,
        user_rsvps=user_rsvps,
        counts=attendance_counts,
        user_total_paid=user_total_paid,
        announcement=announcement,
    )


@app.route("/post_announcement", methods=["POST"])
@admin_required
def post_announcement():
    content = request.form.get("content")
    # Deactivate old announcements first
    Announcements.query.update({Announcements.is_active: False})

    if content:
        new_announcement = Announcements(content=content)
        db.session.add(new_announcement)
        db.session.commit()
        flash("Global announcement updated!")
    return redirect("/admin")


@app.route("/clear_announcement", methods=["POST"])
@admin_required
def clear_announcement():
    Announcements.query.update({Announcements.is_active: False})
    db.session.commit()
    flash("Announcement cleared.")
    return redirect("/admin")


@app.route("/add_event", methods=["GET", "POST"])
@login_required
def add_event():
    if session.get("role") not in ["admin", "supervisor"]:
        flash("Access Denied: Supervisors and Admins only.")
        return redirect("/")
    if request.method == "POST":
        new_event = Events(
            title=request.form.get("title"),
            description=request.form.get("description"),
            event_date=request.form.get("date"),
            event_time=request.form.get("time"),
            location=request.form.get("location"),
            created_by=session["user_id"],
        )
        db.session.add(new_event)
        db.session.commit()
        flash("Event published to the community!")
        return redirect("/")
    return render_template("add_event.html")


@app.route("/edit_event/<int:event_id>", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    if session.get("role") not in ["admin", "supervisor"]:
        flash("Unauthorized")
        return redirect("/")

    event = Events.query.get_or_404(event_id)
    if request.method == "POST":
        event.title = request.form.get("title")
        event.description = request.form.get("description")
        event.event_date = request.form.get("date")
        event.event_time = request.form.get("time")
        event.location = request.form.get("location")
        db.session.commit()
        flash(f"Successfully updated: {event.title}")
        return redirect("/admin")
    return render_template("edit_event.html", event=event)


@app.route("/delete_event/<int:event_id>", methods=["POST"])
@login_required
@admin_required
def delete_event(event_id):
    if session.get("role") not in ["admin", "supervisor"]:
        flash("Access Denied.")
        return redirect("/")

    event = Events.query.get_or_404(event_id)
    RSVP.query.filter_by(event_id=event_id).delete()
    db.session.delete(event)
    db.session.commit()
    flash("Event permanently deleted.")
    return redirect("/admin")


@app.route("/event/<int:event_id>")
@login_required
def event_detail(event_id):
    event = Events.query.get_or_404(event_id)
    attendees = (
        db.session.query(Users).join(RSVP).filter(RSVP.event_id == event_id).all()
    )
    is_going = RSVP.query.filter_by(
        user_id=session["user_id"], event_id=event_id
    ).first()
    return render_template(
        "event_detail.html", event=event, attendees=attendees, is_going=is_going
    )


@app.route("/my_events")
@login_required
def my_events():
    user_id = session.get("user_id")
    # This returns a list of Event objects
    joined_events = (
        db.session.query(Events).join(RSVP).filter(RSVP.user_id == user_id).all()
    )
    return render_template("my_events.html", events=joined_events)


@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    members = Users.query.all()
    events = Events.query.order_by(Events.event_date.desc()).all()

    # --- NEW: Calculate Stats for the top cards ---
    total_members = Users.query.count()
    total_rsvps = RSVP.query.count()
    # Count only users who have been confirmed/assigned as volunteers
    total_volunteers = RSVP.query.filter_by(is_volunteer=True).count()

    # Fetch pending volunteers for the approval section
    pending_volunteers = (
        db.session.query(RSVP, Users, Events)
        .join(Users, RSVP.user_id == Users.id)
        .join(Events, RSVP.event_id == Events.id)
        .filter(RSVP.is_volunteer == True, RSVP.status == "pending")
        .all()
    )

    return render_template(
        "admin_panel.html",
        members=members,
        events=events,
        pending_volunteers=pending_volunteers,
        # --- NEW: Pass these to the HTML ---
        total_members=total_members,
        total_rsvps=total_rsvps,
        total_volunteers=total_volunteers,
    )


@app.route("/apply_to_volunteer/<int:event_id>", methods=["POST"])
@login_required
def apply_to_volunteer(event_id):
    rsvp = RSVP.query.filter_by(user_id=session["user_id"], event_id=event_id).first()
    if rsvp:
        rsvp.is_volunteer = True
        rsvp.status = "pending"  # Keep status pending until Admin approves
        rsvp.volunteer_role = request.form.get("message")
        db.session.commit()
        flash("Your request to volunteer has been sent!")
    return redirect(f"/event/{event_id}")


@app.route("/approve_volunteer/<int:rsvp_id>", methods=["POST"])
@admin_required
def approve_volunteer(rsvp_id):
    rsvp = RSVP.query.get_or_404(rsvp_id)
    rsvp.status = "accepted"  # Approve the volunteer
    db.session.commit()
    flash("Volunteer approved!")
    return redirect("/admin")


@app.route("/reject_volunteer/<int:rsvp_id>", methods=["POST"])
@admin_required
def reject_volunteer(rsvp_id):
    rsvp = RSVP.query.get_or_404(rsvp_id)
    # Option A: Just reset their status
    rsvp.is_volunteer = False
    rsvp.status = "accepted"  # They are still attending, just not volunteering
    rsvp.volunteer_role = None

    db.session.commit()
    flash("Volunteer request declined.")
    return redirect("/admin")


@app.route("/assign_member_to_event", methods=["POST"])
@login_required
def assign_member_to_event():
    if session.get("role") not in ["admin", "supervisor"]:
        flash("Unauthorized access.")
        return redirect("/")

    user_id = request.form.get("user_id")
    event_id = request.form.get("event_id")
    role = request.form.get("volunteer_role")  # Get the role from the modal

    existing = RSVP.query.filter_by(user_id=user_id, event_id=event_id).first()

    if existing:
        existing.is_volunteer = True
        existing.volunteer_role = role
        flash(f"Updated member role to: {role}")
    else:
        new_assignment = RSVP(
            user_id=user_id,
            event_id=event_id,
            status="accepted",
            is_volunteer=True,
            volunteer_role=role,
        )
        db.session.add(new_assignment)
        flash("Member assigned as volunteer.")

    db.session.commit()
    return redirect("/admin")


@app.route("/change_role/<int:user_id>/<string:new_role>", methods=["POST"])
@login_required
def change_role(user_id, new_role):
    # Only the Founder can change roles
    if not session.get("is_founder"):
        flash("Unauthorized!")
        return redirect("/admin")

    user = Users.query.get_or_404(user_id)

    # Prevent the Founder from accidentally demoting themselves
    if user.id == session["user_id"]:
        flash("You cannot change your own role!")
        return redirect("/admin")

    user.role = new_role
    db.session.commit()
    flash(f"Updated {user.username} to {new_role.capitalize()}")
    return redirect("/admin")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.hash, password):
            session["user"] = True
            session["user_id"] = user.id
            session["first_name"] = user.first_name
            session["username"] = user.username
            session["role"] = user.role
            session["is_founder"] = user.is_founder
            return redirect("/")
        flash("Invalid username or password")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u_name = request.form.get("username")
        email = request.form.get("email")
        f_name = request.form.get("first_name")
        l_name = request.form.get("last_name")
        pw = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if Users.query.filter_by(username=u_name).first():
            flash("Username taken.")
            return redirect("/register")

        if pw != confirm:
            flash("Passwords do not match.")
            return redirect("/register")

        # Founder Logic
        is_first = Users.query.count() == 0
        new_user = Users(
            username=u_name,
            email=email,
            first_name=f_name,
            last_name=l_name,
            hash=generate_password_hash(pw),
            role="admin" if is_first else "member",
            is_founder=is_first,
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!")
        return redirect("/login")
    return render_template("register.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = Users.query.get(session["user_id"])
    if request.method == "POST":
        user.first_name = request.form.get("first_name")
        user.last_name = request.form.get("last_name")
        user.email = request.form.get("email")
        db.session.commit()
        session["first_name"] = user.first_name
        flash("Profile updated!")
        return redirect("/profile")
    return render_template("profile.html", user=user)


@app.route("/rsvp/<int:event_id>", methods=["POST"])
@login_required
def rsvp(event_id):
    user_id = session.get("user_id")
    if not RSVP.query.filter_by(user_id=user_id, event_id=event_id).first():
        db.session.add(RSVP(user_id=user_id, event_id=event_id))
        db.session.commit()
        flash("You're on the list!")
    return redirect("/")


@app.route("/cancel_rsvp/<int:event_id>", methods=["POST"])
@login_required
def cancel_rsvp(event_id):
    entry = RSVP.query.filter_by(user_id=session["user_id"], event_id=event_id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
        flash("RSVP cancelled.")
    return redirect("/")


@app.route("/my_payments")
@login_required
def my_payments():
    user_id = session.get("user_id")

    # Fetch all transactions for this user, newest first
    user_payments = (
        Transactions.query.filter_by(user_id=user_id)
        .order_by(Transactions.date_paid.desc())
        .all()
    )

    # Calculate the total amount paid using a simple loop
    total_paid = sum(payment.amount for payment in user_payments)

    return render_template("my_payments.html", payments=user_payments, total=total_paid)


@app.route("/record_payment", methods=["GET", "POST"])
@login_required
def record_payment():
    # 1. Security Check
    if session.get("role") not in ["admin", "treasurer"]:
        flash("Access Denied.")
        return redirect("/")

    # 2. Handle the Form Submission (POST)
    if request.method == "POST":
        user_id = request.form.get("user_id")
        amount = request.form.get("amount")
        purpose = request.form.get("purpose")

        new_trans = Transactions(user_id=user_id, amount=float(amount), purpose=purpose)
        db.session.add(new_trans)
        db.session.commit()
        flash("Payment recorded!")
        return redirect("/admin")

    # 3. Handle showing the page (GET)
    # Fetch the members from the database
    members_list = Users.query.order_by(Users.first_name).all()

    # CRITICAL: 'users' on the left is what the HTML sees.
    # 'members_list' on the right is the data from the line above.
    return render_template("record_payment.html", users=members_list)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
