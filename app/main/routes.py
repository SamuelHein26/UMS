from flask import render_template, request, redirect, url_for, flash
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

@main.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

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
