from flask import render_template, request, redirect, url_for, flash, session
from app.admin import admin
from app.models import db, Person

@admin.route('/dashboard')
def dashboard():
    if session.get('user_role') != 'Admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.index'))
    return render_template('dashboard.html')