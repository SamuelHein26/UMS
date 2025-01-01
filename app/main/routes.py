import re
from flask import render_template, request, redirect, url_for, flash, session
from app.main import main
from app.models import db, Person

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/courses')
def courses():
    return render_template('courses.html')

@main.route('/enroll')
def enroll():
    return render_template('enroll.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']

        # Query the user from the database
        user = Person.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if user and user.check_password(password):
            # Store user info in session
            session['user_id'] = user.person_id
            session['user_role'] = user.role

            # Redirect based on role
            if user.role == 'Admin':
                flash('Welcome, Admin!', 'success')
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'Professor':
                flash('Welcome, Professor!', 'success')
                return redirect(url_for('professor.dashboard'))
            elif user.role == 'Student':
                flash('Welcome, Student!', 'success')
                return redirect(url_for('student.dashboard'))
            else:
                flash('Welcome!', 'success')
                return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('main.login'))
        
    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        #Check password strength
        password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'
        if not re.match(password_pattern, password):
            flash('Password must be at least 8 characters long, include uppercase, lowercase, number, and special character.', 'danger')
            return redirect(url_for('main.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('main.register'))
        
        existing_user = Person.query.filter_by(email=email).first()
        if existing_user:
            flash('This email is already registered', 'danger')
            return redirect(url_for('main.register'))

        new_user = Person(name=name, email=email)
        new_user.set_password(password) #hash the password
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration Successful! Proceed to Login', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            flash('An error occurred while creating account.', 'danger')
            return redirect(url_for('main.register'))
        
    return render_template('register.html')

@main.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/profile')
def profile():
    return render_template('profile.html')