from flask import render_template, request, redirect, url_for, flash, session
from functools import wraps
from app.student import student
from app.models import db

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'Student': 
            flash('Unauthorized access! Student only.', 'danger')
            return redirect(url_for('main.login')) 
        return f(*args, **kwargs)
    return decorated_function

@student.route('/dashboard')
@student_required
def dashboard():
    return render_template('Sdashboard.html')