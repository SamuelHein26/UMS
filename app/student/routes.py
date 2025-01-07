import os
from flask import render_template, request, redirect, url_for, flash, session, current_app
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
from app.student import student
from app.models import db, Student, Enrollment, Course, Exam, Submission

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

@student.route('/enrolled_courses', methods=['GET'])
@student_required
def enrolled_courses():
    # Fetch the logged-in student's studID
    student = Student.query.filter_by(person_id=session['user_id']).first_or_404()

    # Fetch enrollments for the student
    enrollments = (
        Enrollment.query.filter_by(studID=student.studID)
        .join(Course, Enrollment.courseID == Course.courseID)
        .add_columns(
            Enrollment.enrollmentID,
            Course.courseID,
            Course.courseName,
            Course.duration,
            Enrollment.semester,
            Enrollment.status,
            Enrollment.paymentStatus,
            Enrollment.enrollmentDate
        )
        .all()
    )
    
    return render_template('enrolled_courses.html', enrollments=enrollments)

@student.route('/enrolled_courses/drop/<int:enrollmentID>', methods=['POST'])
@student_required
def drop_course(enrollmentID):
    enrollment = Enrollment.query.get_or_404(enrollmentID)

    # Check if the current user owns the enrollment
    student = Student.query.filter_by(person_id=session['user_id']).first()
    if enrollment.studID != student.studID:
        flash('You are not authorized to drop this course.', 'danger')
        return redirect(url_for('student.enrolled_courses'))

    try:
        enrollment.status = 'Dropped'
        enrollment.dropDate = datetime.utcnow()
        db.session.commit()
        flash('Course dropped successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    return redirect(url_for('student.enrolled_courses'))

@student.route('/courses/<string:courseID>/exams', methods=['GET'])
@student_required
def view_exams(courseID):
    # Get the logged-in student's studID
    student = Student.query.filter_by(person_id=session['user_id']).first_or_404()
    print(f"Retrieved studID: {student.studID}")

    # Check if the student is enrolled in the course
    enrollment = Enrollment.query.filter_by(studID=student.studID.strip(), courseID=courseID.strip()).first()
    print(f"Enrollment found: {enrollment}")
    
    if not enrollment:
        flash("You are not enrolled in this course.", "danger")
        return redirect(url_for('student.enrolled_courses'))

    # Fetch exams for the enrolled course
    exams = Exam.query.filter_by(courseID=courseID).all()
    
    return render_template('view_exams.html', exams=exams, courseID=courseID)


@student.route('/exams/<int:examID>/submit', methods=['GET', 'POST'])
@student_required
def submit_assignment(examID):
    exam = Exam.query.get_or_404(examID)
    if exam.examType != 'Assignment':
        flash('This exam is not an assignment.', 'danger')
        return redirect(url_for('student.view_exams', courseID=exam.courseID))

    student = Student.query.filter_by(person_id=session['user_id']).first_or_404()

    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            flash('No file selected for upload.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        filename = secure_filename(f"{student.studID}_{examID}_{file.filename}")
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        print(f"Saving file to: {file_path}")  # Debugging output

        try:
            file.save(file_path)
            new_submission = Submission(
                examID=examID,
                studID=student.studID,
                file_path=file_path,
                submitted_at=datetime.utcnow()
            )
            db.session.add(new_submission)
            db.session.commit()
            flash('Assignment submitted successfully!', 'success')
            return redirect(url_for('student.view_exams', courseID=exam.courseID))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while submitting the assignment: {str(e)}', 'danger')

    return render_template('submit_assignment.html', exam=exam)

