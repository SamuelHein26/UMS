from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
from app import db

# Person Table
class Person(db.Model):
    __tablename__ = 'Person'
    person_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('Admin', 'Student', 'Professor', 'User'), nullable=False, default='User')
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(
        db.Enum('Male', 'Female', 'Other', 'Prefer not to say'), 
        default='Prefer not to say'
    )
    phone_no = db.Column(db.String(15), unique=True, nullable=True)
    dob = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, raw_password):
        """Hash the password using bcrypt."""
        hashed = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed.decode('utf-8')

    def check_password(self, raw_password):
        """Check if the raw password matches the stored hash."""
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    def __repr__(self):
        return f"<Person(id={self.person_id}, name={self.name})>"

# Address Table
class Address(db.Model):
    __tablename__ = 'Address'
    addressID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.Integer, db.ForeignKey('Person.person_id', ondelete='CASCADE'), nullable=False)
    street = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Student Table
class Student(db.Model):
    __tablename__ = 'Student'
    person_id = db.Column(db.Integer, db.ForeignKey('Person.person_id', ondelete='CASCADE'), nullable=False)
    studID = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    courses = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Professor Table
class Professor(db.Model):
    __tablename__ = 'Professor'
    person_id = db.Column(db.Integer, db.ForeignKey('Person.person_id', ondelete='CASCADE'), nullable=False)
    profID = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    department_id = db.Column(db.String(20), db.ForeignKey('Department.departmentID', ondelete='CASCADE'), nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Admin Table
class Admin(db.Model):
    __tablename__ = 'Admin'
    person_id = db.Column(db.Integer, db.ForeignKey('Person.person_id', ondelete='CASCADE'), nullable=False)
    adminID = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=True)
    stu_start_date = db.Column(db.Date, nullable=True)
    prof_start_date = db.Column(db.Date, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Department Table
class Department(db.Model):
    __tablename__ = 'Department'
    departmentID = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    contactInfo = db.Column(db.String(100), nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Course Table
class Course(db.Model):
    __tablename__ = 'Course'
    courseID = db.Column(db.String(20), primary_key=True)
    courseName = db.Column(db.String(100), nullable=False)
    departmentID = db.Column(db.String(20), db.ForeignKey('Department.departmentID', ondelete='CASCADE'), nullable=False)
    duration = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Enrollment Table
class Enrollment(db.Model):
    __tablename__ = 'Enrollment'
    enrollmentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    studID = db.Column(db.String(20), db.ForeignKey('Student.studID', ondelete='CASCADE'), nullable=False)
    courseID = db.Column(db.String(20), db.ForeignKey('Course.courseID', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=True)
    enrollmentDate = db.Column(db.DateTime, nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    dropDate = db.Column(db.DateTime, nullable=True)
    paymentStatus = db.Column(db.Boolean, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Attendance Table
class Attendance(db.Model):
    __tablename__ = 'Attendance'
    attendanceID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    studID = db.Column(db.String(20), db.ForeignKey('Student.studID', ondelete='CASCADE'), nullable=False)
    profID = db.Column(db.String(20), db.ForeignKey('Professor.profID', ondelete='CASCADE'), nullable=False)
    courseID = db.Column(db.String(20), db.ForeignKey('Course.courseID', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Boolean, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Fee Table
class Fee(db.Model):
    __tablename__ = 'Fee'
    feeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollmentID = db.Column(db.Integer, db.ForeignKey('Enrollment.enrollmentID', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    dueDate = db.Column(db.DateTime, nullable=False)
    paymentMethod = db.Column(db.Enum('Credit Card', 'Bank Transfer', 'Cash', 'Other'), nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Exam Table
class Exam(db.Model):
    __tablename__ = 'Exam'
    examID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    courseID = db.Column(db.String(20), db.ForeignKey('Course.courseID', ondelete='CASCADE'), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    examType = db.Column(db.Enum('Assignment', 'Written'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    maxMarks = db.Column(db.Float, nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Grade Table
class Grade(db.Model):
    __tablename__ = 'Grade'
    gradeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    courseID = db.Column(db.String(20), db.ForeignKey('Course.courseID', ondelete='CASCADE'), nullable=False)
    studID = db.Column(db.String(20), db.ForeignKey('Student.studID', ondelete='CASCADE'), nullable=False)
    examID = db.Column(db.Integer, db.ForeignKey('Exam.examID', ondelete='CASCADE'), nullable=True)
    grade = db.Column(db.Float, nullable=False)
    gradeCategory = db.Column(db.Enum('Assignment', 'Exam'), nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
