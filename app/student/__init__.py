from flask import Blueprint

student = Blueprint('student', __name__, template_folder='templates')

from app.student import routes
