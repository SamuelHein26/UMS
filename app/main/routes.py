import re
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, session
from app.main import main
from app.models import db, Person, Professor, Student, Address, Course, Enrollment, Fee

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/courses', methods=['GET'])
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@main.route('/enroll/<string:courseID>', methods=['GET', 'POST'])
def enroll(courseID):
    if 'user_id' not in session:
        flash('You need to be logged in to enroll in a course.', 'warning')
        return redirect(url_for('main.courses'))

    user_id = session['user_id']
    user = Person.query.get(user_id)

    if user.role != 'User':
        flash('You are already a student or have another role!', 'danger')
        return redirect(url_for('main.courses'))

    course = Course.query.get(courseID)
    if not course:
        flash('Course not found!', 'danger')
        return redirect(url_for('main.courses'))

    # Check if a minimal Student record already exists
    student = Student.query.filter_by(person_id=user_id).first()
    if not student:
        studID = f"STU{user_id}"
        student = Student(person_id=user_id, studID=studID)
        db.session.add(student)
        db.session.commit()  # Commit to ensure the Student record is saved

    if request.method == 'POST':
        semester = request.form.get('semester')

        # Create Enrollment record
        enrollment = Enrollment(
            studID=student.studID,
            courseID=courseID,
            status="Pending Payment",
            enrollmentDate=datetime.utcnow(),
            semester=semester,
            paymentStatus=False
        )

        try:
            db.session.add(enrollment)
            db.session.commit()
            flash(f'Enrollment initiated for {course.courseName}. Please proceed to payment.', 'success')
            return redirect(url_for('main.payment', enrollmentID=enrollment.enrollmentID))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during enrollment: {str(e)}', 'danger')
            return redirect(url_for('main.enroll', courseID=courseID))

    return render_template('enroll.html', course=course, user=user)


@main.route('/payment/<int:enrollmentID>', methods=['GET', 'POST'])
def payment(enrollmentID):
    if 'user_id' not in session:
        flash('You need to be logged in to proceed with payment.', 'warning')
        return redirect(url_for('main.courses'))

    enrollment = Enrollment.query.get(enrollmentID)
    if not enrollment:
        flash('Enrollment not found. Please try again.', 'danger')
        return redirect(url_for('main.courses'))

    if enrollment.paymentStatus:
        flash('Payment has already been completed for this enrollment.', 'info')
        return redirect(url_for('student.dashboard'))

    course = Course.query.get(enrollment.courseID)
    if not course:
        flash('Course not found. Please contact support.', 'danger')
        return redirect(url_for('main.courses'))

    if request.method == 'POST':
        paymentMethod = request.form.get('paymentMethod')

        # Create Fee record
        fee = Fee(
            enrollmentID=enrollmentID,
            amount=course.courseFee,
            dueDate=datetime.utcnow() + timedelta(days=7),
            paymentMethod=paymentMethod
        )
        enrollment.paymentStatus = True
        enrollment.status = "Active"

        # Update user role to Student
        user = Person.query.get(session['user_id'])
        user.role = 'Student'

        # Update the Student record with additional details
        student = Student.query.filter_by(person_id=user.person_id).first()
        student.courses = course.courseName

        try:
            db.session.add(fee)
            db.session.commit()
            flash('Payment successful! You are now enrolled as a student. Please Log in again to access student dashboard!', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during payment: {str(e)}', 'danger')
            return redirect(url_for('main.payment', enrollmentID=enrollmentID))

    return render_template('payment.html', enrollment=enrollment, course=course)

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
    # Fetch the currently logged-in user
    user_id = session.get('user_id')
    user = Person.query.get(user_id)

    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('main.login'))

    # Fetch address details
    address = Address.query.filter_by(person_id=user.person_id).first()

    # Prepare role-specific data
    role_specific_data = {}
    if user.role == 'Professor':
        professor = Professor.query.filter_by(person_id=user.person_id).first()
        role_specific_data['professor'] = professor
    elif user.role == 'Student':
        student = Student.query.filter_by(person_id=user.person_id).first()
        role_specific_data['student'] = student
    elif user.role == 'Admin':
        role_specific_data['admin'] = True

    return render_template(
        'profile.html',
        user=user,
        address=address,
        role_data=role_specific_data
    )

@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    user = Person.query.get(user_id)
    address = Address.query.filter_by(person_id=user_id).first()

    if request.method == 'POST':
        # Update user fields
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone_no = request.form.get('phone_no')
        user.age = request.form.get('age')
        user.gender = request.form.get('gender')

        # Update or create address
        if not address:
            address = Address(person_id=user_id)
            db.session.add(address)

        address.street = request.form.get('street')
        address.city = request.form.get('city')
        address.state = request.form.get('state')
        address.postal_code = request.form.get('postal_code')
        address.country = request.form.get('country')

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')

    return render_template('edit_profile.html', user=user, address=address)

@main.route('/redirect_back')
def redirect_back():
    role = session.get('user_role')

    if role == 'Admin':
        return redirect(url_for('admin.dashboard'))
    elif role == 'Professor':
        return redirect(url_for('professor.dashboard'))
    elif role == 'Student':
        return redirect(url_for('student.dashboard'))
    else:
        return redirect(url_for('main.index'))