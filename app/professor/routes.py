import os
from flask import render_template, request, redirect, url_for, flash, session, current_app
from functools import wraps
from app.professor import professor
from app.models import db, Professor, Person, Enrollment, Course, Exam, Submission, Attendance, Student


def professor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'Professor': 
            flash('Unauthorized access! Professor only.', 'danger')
            return redirect(url_for('main.login')) 
        return f(*args, **kwargs)
    return decorated_function

@professor.route('/dashboard')
@professor_required
def dashboard():
    return render_template('Pdashboard.html')

@professor.route('/courses', methods=['GET'])
@professor_required
def view_courses():
    professor = Professor.query.filter_by(person_id=session['user_id']).first_or_404()
    courses = Course.query.filter_by(departmentID=professor.department_id).all()
    return render_template('view_courses.html', courses=courses)


@professor.route('/courses/<string:courseID>/exams', methods=['GET'])
@professor_required
def view_course_exams(courseID):
    exams = Exam.query.filter_by(courseID=courseID).all()
    course = Course.query.get_or_404(courseID)
    return render_template('view_course_exams.html', exams=exams, course=course)

@professor.route('/courses/<string:courseID>/create_exam', methods=['GET', 'POST'])
@professor_required
def create_exam(courseID):
    course = Course.query.get_or_404(courseID)

    if request.method == 'POST':
        examType = request.form['examType']
        date = request.form['date']
        maxMarks = request.form['maxMarks']

        # Default values for assignments
        location = request.form.get('location') if examType == 'Written' else "N/A"
        duration = request.form.get('duration') if examType == 'Written' else 0

        new_exam = Exam(
            courseID=courseID,
            examType=examType,
            date=date,
            location=location,
            duration=duration,
            maxMarks=maxMarks
        )

        try:
            db.session.add(new_exam)
            db.session.commit()
            flash(f'{examType} created successfully for {course.courseName}!', 'success')
            return redirect(url_for('professor.view_course_exams', courseID=courseID))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('create_exam.html', course=course)


@professor.route('/exams/edit/<int:examID>', methods=['GET', 'POST'])
@professor_required
def edit_exam(examID):
    exam = Exam.query.get_or_404(examID)

    if request.method == 'POST':
        exam.examType = request.form['examType']
        exam.date = request.form['date']
        exam.maxMarks = request.form['maxMarks']
        exam.location = request.form.get('location') if exam.examType == 'Written' else None
        exam.duration = request.form.get('duration') if exam.examType == 'Written' else None

        try:
            db.session.commit()
            flash('Exam updated successfully!', 'success')
            return redirect(url_for('professor.view_course_exams', courseID=exam.courseID))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('edit_exam.html', exam=exam)

@professor.route('/professor/delete/<int:examID>', methods=['POST'])
@professor_required
def delete_exam(examID):
    exam = Exam.get(examID)
    db.session.delete(exam)
    db.session.commit()
    flash('Exam deleted successfully!', 'success')
    return redirect(url_for('professor.view_course_exams'))

@professor.route('/exams/<int:examID>/submissions', methods=['GET'])
@professor_required
def view_submissions(examID):
    exam = Exam.query.get_or_404(examID)
    submissions = Submission.query.filter_by(examID=examID).all()
    return render_template('view_submissions.html', exam=exam, submissions=submissions)


