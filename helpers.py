from flask import redirect, session, flash
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            flash("Please log in to access this page.")
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorate routes to require admin role.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Access denied: Admins only.")
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function
