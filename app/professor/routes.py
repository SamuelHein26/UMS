import os
from flask import render_template, request, redirect, url_for, flash, session, current_app
from functools import wraps
from datetime import datetime
from app.professor import professor
from app.models import db, Professor, Course, Exam, Submission, Attendance, Grade, Enrollment


def professor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'Professor': 
            flash('Unauthorized access! Professor only.', 'danger')
            return redirect(url_for('main.profile')) 
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

    # Handle form submission
    if request.method == 'POST':
        examType = request.form['examType']
        location = request.form['location']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        duration = int(request.form['duration'])
        maxMarks = float(request.form['maxMarks'])

        exam.examType = examType
        exam.location = location
        exam.date = date
        exam.duration = duration
        exam.maxMarks = maxMarks

        try:
            db.session.commit()
            flash('Exam updated successfully!', 'success')
            return redirect(url_for('professor.view_course_exams', courseID=exam.courseID))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while updating the exam: {str(e)}', 'danger')

    return render_template('edit_exam.html', exam=exam)


@professor.route('/exams/delete/<int:examID>', methods=['POST'])
@professor_required
def delete_exam(examID):
    exam = Exam.query.get_or_404(examID)

    try:
        db.session.delete(exam)
        db.session.commit()
        flash('Exam deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the exam: {str(e)}', 'danger')

    return redirect(url_for('professor.view_course_exams', courseID=exam.courseID))

@professor.route('/exams/<int:examID>/submissions', methods=['GET'])
@professor_required
def view_submissions(examID):
    exam = Exam.query.get_or_404(examID)

    submissions = (
        db.session.query(Submission, Grade)
        .outerjoin(Grade, (Submission.examID == Grade.examID) & (Submission.studID == Grade.studID))
        .filter(Submission.examID == examID)
        .all()
    )

    return render_template('view_submissions.html', submissions=submissions, exam=exam)


@professor.route('/submissions/<int:submissionID>/mark', methods=['GET', 'POST'])
@professor_required
def mark_submission(submissionID):
    # Retrieve the submission and associated exam details
    submission = Submission.query.get_or_404(submissionID)
    exam = Exam.query.get_or_404(submission.examID)

    if request.method == 'POST':
        grade_value = float(request.form['grade']) 

        # Check if a grade already exists for this submission
        grade = Grade.query.filter_by(studID=submission.studID, examID=submission.examID).first()

        try:
            if grade_value > 100:
                flash('Error: Grade must not be over 100.', 'danger')
                return redirect(url_for('professor.mark_submission', submissionID=submission.submissionID))
            
            if grade:
                # Update existing grade
                grade.grade = grade_value
            else:
                # Insert new grade
                new_grade = Grade(
                    courseID=exam.courseID,
                    studID=submission.studID,
                    examID=submission.examID,
                    grade=grade_value,
                    gradeCategory=exam.examType,
                )
                db.session.add(new_grade)

            db.session.commit()
            flash('Submission marked successfully!', 'success')
            return redirect(url_for('professor.view_submissions', examID=submission.examID))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while marking the submission: {str(e)}', 'danger')

    return render_template('mark_submission.html', submission=submission, exam=exam)

@professor.route('/courses/<string:courseID>/attendance', methods=['GET', 'POST'])
@professor_required
def mark_attendance(courseID):
    course = Course.query.get_or_404(courseID)

    # Query the professor using session user_id
    professor = Professor.query.filter_by(person_id=session['user_id']).first_or_404()

    enrollments = Enrollment.query.filter_by(courseID=courseID, status='Active').all()

    # Get the current date in 'YYYY-MM-DD' format
    current_date = datetime.utcnow().strftime('%Y-%m-%d')

    if request.method == 'POST':
        attendance_date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        present_students = request.form.getlist('present')

        try:
            for enrollment in enrollments:
                studID = enrollment.studID
                status = studID in present_students  # Mark as present if in the list

                # Create attendance record
                new_attendance = Attendance(
                    studID=studID,
                    profID=professor.profID,  # Use the correct profID
                    courseID=courseID,
                    date=attendance_date,
                    status=status
                )
                db.session.add(new_attendance)

            db.session.commit()
            flash('Attendance marked successfully!', 'success')
            return redirect(url_for('professor.view_courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while marking attendance: {str(e)}', 'danger')

    return render_template('mark_attendance.html', course=course, enrollments=enrollments, current_date=current_date)


