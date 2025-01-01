from flask import Blueprint

professor = Blueprint('professor', __name__, template_folder='templates')

from app.professor import routes
