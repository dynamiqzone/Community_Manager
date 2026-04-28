from flask import redirect, session, flash
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add supervisor and treasurer here so they aren't blocked!
        if session.get("role") not in ["admin", "supervisor", "treasurer"]:
            flash("Unauthorized access!")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function