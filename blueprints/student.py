from curses import flash
from flask import Blueprint, redirect, render_template, request, session
import services.courses as course_service
import services.free_form_tasks as free_form_task_service
import services.multiple_choice_tasks as multiple_choice_task_service

student = Blueprint("student", __name__)


@student.route('/course_page', methods=['GET'])
def course_page():
    course_id = request.args.get('course_id')
    user_id = session.get('user_id')
    course = course_service.get(course_id)
    materials = course_service.get_materials(course_id)
    free_form_tasks = free_form_task_service.get(course_id)
    free_form_submissions = free_form_task_service.get_submissions(user_id, course_id)
    multiple_choice_tasks = multiple_choice_task_service.get_without_answers(course_id)
    multiple_choice_submissions = multiple_choice_task_service.get_submissions(user_id, course_id)
    return render_template(
        'student/course_page.html',
        course=course,
        materials=materials,
        free_form_tasks=free_form_tasks,
        free_form_submissions=free_form_submissions,
        multiple_choice_tasks=multiple_choice_tasks,
        multiple_choice_submissions=multiple_choice_submissions)


@student.route('/add_new_multiple_choice_task_submission', methods=['POST'])
def add_new_multiple_choice_task_submission():
    if "username" not in session:
        flash('Kirjaudu sisään vastataksesi tehtäviin', 'error')
        return redirect("/")

    if session.get('is_teacher'):
        flash('Opettajat eivät voi vastata opiskelijoiden tehtäviin', 'error')
        return redirect("/")

    course_id = request.form['course_id']
    task_id = request.form['task_id']
    student_user_id = session['user_id']
    submission = multiple_choice_task_service.parse_submission(request)
    multiple_choice_task_service.create_submission(student_user_id, task_id, submission)
    return redirect(f'/course_page?course_id={course_id}')


@student.route('/add_new_free_form_task_submission', methods=['POST'])
def add_new_free_form_task_submission():
    if "username" not in session:
        flash('Kirjaudu sisään vastataksesi tehtäviin', 'error')
        return redirect("/")

    if session.get('is_teacher'):
        flash('Opettajat eivät voi vastata opiskelijoiden tehtäviin', 'error')
        return redirect("/")

    course_id = request.form['course_id']
    task_id = request.form['task_id']
    answer = request.form['answer']
    student_user_id = session.get('user_id')
    free_form_task_service.create_submission(student_user_id, task_id, answer)
    return redirect(f'/course_page?course_id={course_id}')