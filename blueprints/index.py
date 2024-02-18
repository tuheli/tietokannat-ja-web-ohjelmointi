from flask import Blueprint, render_template, session

import services.courses as course_service

index = Blueprint("index", __name__)


@index.route("/")
def intial_route():
    if "username" not in session:
        return render_template("auth/login.html")

    user_id = session.get("user_id")
    users_courses = course_service.get_users_courses(user_id)

    if session.get('is_teacher'):
        return render_template(
            "teacher/dashboard.html",
            courses=users_courses)
    else:
        available_courses = course_service.get_joinable_courses(user_id)
        return render_template(
            "student/dashboard.html",
            joined_courses=users_courses,
            available_courses=available_courses)
