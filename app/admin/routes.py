from flask import render_template, request, redirect, url_for, flash, session
from functools import wraps
from app.admin import admin
from app.models import db, Student, Professor, Course, Department, Person

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'Admin': 
            flash('Unauthorized access! Admins only.', 'danger')
            return redirect(url_for('main.login')) 
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@admin_required
def dashboard():
    return render_template('dashboard.html')

#################################################################################################
# View Routes
@admin.route('/students')
@admin_required
def view_students():
    students = Student.query.all()
    return render_template('students/view_students.html', students=students)

@admin.route('/professors')
@admin_required
def view_professors():
    professors = Professor.query.all()
    return render_template('professors/view_professors.html', professors=professors)

@admin.route('/courses')
@admin_required
def view_courses():
    courses = Course.query.all()
    return render_template('courses/view_courses.html', courses=courses)

@admin.route('/departments')
@admin_required
def view_departments():
    departments = Department.query.all()
    return render_template('departments/view_departments.html', departments=departments)

@admin.route('/users')
@admin_required
def view_users():
    users = Person.query.all()
    return render_template('users/view_users.html', users=users)

#################################################################################################

# Add Routes
@admin.route('/students/add', methods=['GET', 'POST'])
@admin_required
def add_student():
    if request.method == 'POST':
        person_id = request.form['person_id']
        studID = request.form['studID']
        courses = request.form.getlist('courses')

        new_student = Student(person_id=person_id, studID=studID, courses=','.join(courses))
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('admin.view_students'))

    return render_template('students/add_student.html')

@admin.route('/professors/add', methods=['GET', 'POST'])
@admin_required
def add_professor():
    if request.method == 'POST':
        person_id = request.form.get('person_id')
        profID = request.form.get('profID')
        department_id = request.form.get('department_id')

        # Validate person_id
        person = Person.query.get(person_id)
        if not person:
            flash('Invalid person ID. No such person exists.', 'danger')
            return redirect(url_for('admin.add_professor'))

        # Check if person is already a professor
        existing_professor = Professor.query.filter_by(person_id=person_id).first()
        if existing_professor:
            flash('This person is already assigned as a professor.', 'danger')
            return redirect(url_for('admin.add_professor'))

        # Validate unique profID
        existing_profID = Professor.query.filter_by(profID=profID).first()
        if existing_profID:
            flash('Professor ID already exists. Please use a unique ID.', 'danger')
            return redirect(url_for('admin.add_professor'))

        # Validate department_id
        department = Department.query.get(department_id)
        if not department:
            flash('Invalid department ID. No such department exists.', 'danger')
            return redirect(url_for('admin.add_professor'))

        # Add the new professor
        new_professor = Professor(person_id=person_id, profID=profID, department_id=department_id)

        try:
            # Update the person's role to 'Professor'
            person.role = 'Professor'
            
            db.session.add(new_professor)
            db.session.commit()
            flash('Professor added successfully!', 'success')
            return redirect(url_for('admin.view_professors'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the professor. Please try again.', 'danger')
            return redirect(url_for('admin.add_professor'))

    # Fetch departments for the form
    departments = Department.query.all()
    
        # Fetch persons who are not already professors and have the 'User' role
    available_persons = Person.query.filter(
        ~Person.person_id.in_(db.session.query(Professor.person_id)),
        Person.role == 'User'
    ).all()

    return render_template(
        'professors/add_professor.html',
        departments=departments,
        available_persons=available_persons
    )


@admin.route('/courses/add', methods=['GET', 'POST'])
@admin_required
def add_course():
    if request.method == 'POST':
        courseID = request.form.get('courseID')
        courseName = request.form.get('courseName')
        departmentID = request.form.get('departmentID')
        duration = request.form.get('duration')
        description = request.form.get('description')

        # Validate unique course ID
        existing_course = Course.query.filter_by(courseID=courseID).first()
        if existing_course:
            flash('Course ID already exists. Please use a unique ID.', 'danger')
            return redirect(url_for('admin.add_course'))

        # Validate department
        department = Department.query.get(departmentID)
        if not department:
            flash('Invalid department ID. No such department exists.', 'danger')
            return redirect(url_for('admin.add_course'))

        # Add the new course
        new_course = Course(
            courseID=courseID,
            courseName=courseName,
            departmentID=departmentID,
            duration=duration,
            description=description
        )
        try:
            db.session.add(new_course)
            db.session.commit()
            flash('Course added successfully!', 'success')
            return redirect(url_for('admin.view_courses'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the course. Please try again.', 'danger')
            return redirect(url_for('admin.add_course'))

    departments = Department.query.all()  # Fetch departments for the dropdown
    return render_template('courses/add_course.html', departments=departments)


@admin.route('/departments/add', methods=['GET', 'POST'])
@admin_required
def add_department():
    if request.method == 'POST':
        departmentID = request.form['departmentID']
        name = request.form['name']
        location = request.form['location']
        contactInfo = request.form['contactInfo']

        new_department = Department(departmentID=departmentID, name=name, location=location, contactInfo=contactInfo)
        db.session.add(new_department)
        db.session.commit()
        flash('Department added successfully!', 'success')
        return redirect(url_for('admin.view_departments'))

    return render_template('departments/add_department.html')

#################################################################################################

# Edit Routes
@admin.route('/students/edit/<string:studID>', methods=['GET', 'POST'])
@admin_required
def edit_student(studID):
    student = Student.query.get(studID)
    if request.method == 'POST':
        student.courses = ','.join(request.form.getlist('courses'))
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('admin.view_students'))

    return render_template('students/edit_student.html', student=student)

@admin.route('/professors/edit/<string:profID>', methods=['GET', 'POST'])
@admin_required
def edit_professor(profID):
    professor = Professor.query.get(profID)
    if not professor:
        flash('Professor not found!', 'danger')
        return redirect(url_for('admin.view_professors'))

    departments = Department.query.all()

    if request.method == 'POST':
        professor.person.name = request.form['name']
        professor.department_id = request.form['department_id']
        professor.person.email = request.form['email']
        professor.person.phone_no = request.form.get('phone_no')
        try:
            db.session.commit()
            flash('Professor updated successfully!', 'success')
            return redirect(url_for('admin.view_professors'))
        except Exception as e:
            flash('An error occurred while updating the professor.', 'danger')
            return redirect(url_for('admin.edit_professor', profID=profID))

    return render_template('professors/edit_professor.html', professor=professor, departments=departments)


@   admin.route('/courses/edit/<string:courseID>', methods=['GET', 'POST'])
@admin_required
def edit_course(courseID):
    course = Course.query.get(courseID)
    if not course:
        flash('Course not found!', 'danger')
        return redirect(url_for('admin.view_courses'))

    departments = Department.query.all()

    if request.method == 'POST':
        course.courseName = request.form['courseName']
        course.departmentID = request.form['departmentID']
        course.duration = request.form['duration']
        course.description = request.form['description']

        try:
            db.session.commit()
            flash('Course updated successfully!', 'success')
            return redirect(url_for('admin.view_courses'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the course. Please try again.', 'danger')

    return render_template('courses/edit_course.html', course=course, departments=departments)

@admin.route('/departments/edit/<string:departmentID>', methods=['GET', 'POST'])
@admin_required
def edit_department(departmentID):
    department = Department.query.get(departmentID)
    if not department:
        flash('Department not found!', 'danger')
        return redirect(url_for('admin.view_departments'))

    if request.method == 'POST':
        department.name = request.form['name']
        department.location = request.form['location']
        department.contactInfo = request.form['contactInfo']
        try:
            db.session.commit()
            flash('Department updated successfully!', 'success')
            return redirect(url_for('admin.view_departments'))
        except Exception as e:
            flash('An error occurred while updating the department.', 'danger')
            return redirect(url_for('admin.edit_department', departmentID=departmentID))

    return render_template('departments/edit_department.html', department=department)

@admin.route('/users/edit/<int:person_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(person_id):
    user = Person.query.get(person_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin.view_users'))

    if request.method == 'POST':
        user.name = request.form['name']
        user.role = request.form['role']
        user.age = request.form.get('age')
        user.gender = request.form.get('gender')
        user.phone_no = request.form.get('phone_no')
        user.dob = request.form.get('dob')
        user.email = request.form['email']
        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.view_users'))
        except Exception as e:
            flash('An error occurred while updating the user.', 'danger')
            return redirect(url_for('admin.edit_user', person_id=person_id))

    return render_template('users/edit_user.html', user=user)

#################################################################################################

# Delete Routes
@admin.route('/students/delete/<string:studID>', methods=['POST'])
@admin_required
def delete_student(studID):
    student = Student.query.get(studID)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('admin.view_students'))

@admin.route('/professors/delete/<string:profID>', methods=['POST'])
@admin_required
def delete_professor(profID):
    professor = Professor.query.get(profID)
    db.session.delete(professor)
    db.session.commit()
    flash('Professor deleted successfully!', 'success')
    return redirect(url_for('admin.view_professors'))

@admin.route('/courses/delete/<string:courseID>', methods=['POST'])
@admin_required
def delete_course(courseID):
    course = Course.query.get(courseID)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin.view_courses'))

@admin.route('/departments/delete/<string:departmentID>', methods=['POST'])
@admin_required
def delete_department(departmentID):
    department = Department.query.get(departmentID)
    db.session.delete(department)
    db.session.commit()
    flash('Department deleted successfully!', 'success')
    return redirect(url_for('admin.view_departments'))

@admin.route('/users/delete/<int:person_id>', methods=['POST'])
@admin_required
def delete_user(person_id):
    user = Person.query.get(person_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin.view_users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
        return redirect(url_for('admin.view_users'))
    except Exception as e:
        flash('An error occurred while deleting the user.', 'danger')
        return redirect(url_for('admin.view_users'))

#################################################################################################