from flask import Blueprint, render_template
from app.main import main

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
    return render_template('register.html')
