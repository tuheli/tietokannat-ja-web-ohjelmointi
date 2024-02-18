from os import getenv
from flask import Flask
from db import db

from blueprints.index import index
from blueprints.teacher import teacher
from blueprints.auth import auth
from blueprints.student import student
from blueprints.course import course

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

db.init_app(app)

app.register_blueprint(index)
app.register_blueprint(teacher)
app.register_blueprint(auth)
app.register_blueprint(student)
app.register_blueprint(course)
