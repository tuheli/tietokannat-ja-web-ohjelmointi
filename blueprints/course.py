from flask import Blueprint, abort, redirect, request, session
from sqlalchemy.sql import text
from app import db

course = Blueprint("course", __name__)


@course.route('/join_course', methods=['POST'])
def join_course():
    if not session.get('username'):
        return redirect("Vain kirjautuneet käyttäjät voivat liittyä kurssille")
    
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    
    course_id = request.form['course_id']
    sql = text(
        "INSERT INTO user_courses (user_id, course_id) VALUES (:user_id, :course_id)")
    db.session.execute(sql, {"user_id": session.get(
        "user_id"), "course_id": course_id})
    db.session.commit()
    return redirect('/')
