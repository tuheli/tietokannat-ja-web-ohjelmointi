from flask import Blueprint, abort, flash, redirect, render_template, request, session
import services.courses as course_service
import services.multiple_choice_tasks as multiple_choice_task_service
import services.free_form_tasks as free_form_task_service
import services.statistics as statistics_service

teacher = Blueprint("teacher", __name__)


@teacher.route('/edit_course', methods=['GET'])
def edit_course():
    if not session.get('is_teacher'):
        flash('Vain opettajat voivat muokata kursseja', 'error')
        return redirect('/')

    course_id = request.args.get('course_id')
    option_count = request.args.get('option_count', default=4, type=int)
    course = course_service.get(course_id)
    materials = course_service.get_materials(course_id)
    students = statistics_service.get_students_with_submissions(course_id)
    multiple_choice_tasks = multiple_choice_task_service.get(course_id)
    free_form_tasks = free_form_task_service.get(course_id)
    course_statistics = statistics_service.get_course_statistics(course_id)
    return render_template(
        'teacher/edit_course.html',
        course=course,
        materials=materials,
        students=students,
        option_count=option_count,
        multiple_choice_tasks=multiple_choice_tasks,
        free_form_tasks=free_form_tasks,
        course_statistics=course_statistics)


@teacher.route('/create_course', methods=['POST'])
def create_course():
    if not session.get('username'):
        flash('Vain kirjautuneet käyttäjät voivat luoda kursseja', 'error')
        return redirect('/')

    if not session.get('is_teacher'):
        flash('Vain opettajat voivat luoda kursseja', 'error')
        return redirect('/')
    
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    title = request.form['title']
    description = request.form['description']

    if not course_service.is_valid_course(title, description):
        flash('Kurssin tiedot eivät kelpaa', 'error')
        return redirect('/')

    course_service.create(session.get('user_id'), title, description)
    flash('Kurssin luonti onnistui', 'success')
    return redirect('/')


@teacher.route('/update_course_materials', methods=['POST'])
def update_course_materials():
    if not session.get('username'):
        flash('Vain kirjautuneet käyttäjät voivat muokata kursseja', 'error')
        return redirect('/')

    if not session.get('is_teacher'):
        flash('Vain opettajat voivat muokata kursseja', 'error')
        return redirect('/')
    
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    course_id = request.form['course_id']
    materials = request.form['materials']

    course_service.update_materials(course_id, materials)
    flash('Kurssimateriaali päivitetty onnistuneesti.', 'success')
    return redirect(f'/edit_course?course_id={course_id}')


@teacher.route('/delete_course', methods=['POST'])
def delete_course():
    if not session.get('username'):
        flash('Vain kirjautuneet käyttäjät voivat poistaa kursseja', 'error')
        return redirect('/')

    if not session.get('is_teacher'):
        flash('Vain opettajat voivat poistaa kursseja', 'error')
        return redirect('/')
    
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    course_id = request.form['course_id']
    course_service.delete(course_id)
    return redirect('/')


@teacher.route('/update_course_title', methods=['POST'])
def update_course_title():
    if not session.get('username'):
        flash('Vain kirjautuneet käyttäjät voivat muokata kursseja', 'error')
        return redirect('/')

    if not session.get('is_teacher'):
        flash('Vain opettajat voivat muokata kursseja', 'error')
        return redirect('/')
    
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    course_id = request.form['course_id']
    new_title = request.form['new_title']
    was_update_successful = course_service.update_title(course_id, new_title)

    if was_update_successful:
        flash('Kurssin nimi päivitettiin onnistuneesti', 'success')
        return redirect(f'/edit_course?course_id={course_id}')
    else:
        flash(
            'Kurssin nimen päivitys epäonnistui. Nimen tulee olla määritelty ja se saa olla enintään 255 merkkiä pitkä.',
            'error')
        return redirect(f'/edit_course?course_id={course_id}')
    

@teacher.route('/add_new_multiple_choice_task', methods=['POST'])
def add_new_multiple_choice_task():
    if not session.get('username'):
        flash('Vain kirjautuneet käyttäjät voivat lisätä tehtäviä', 'error')
        return redirect('/')
    
    if not session.get('is_teacher'):
        flash('Vain opettajat voivat lisätä tehtäviä', 'error')
        return redirect('/')
    
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    course_id = request.form['course_id']
    question = request.form['question']

    if not question:
        flash("Kysymys puuttuu", "error")
        return redirect(f'/edit_course?course_id={course_id}')

    option_count = request.form['option_count']
    options = multiple_choice_task_service.parse_options(request)
    multiple_choice_task_service.create_task(course_id, question, options)
    return redirect(
        f'/edit_course?course_id={course_id}&option_count={option_count}')

@teacher.route('/add_new_free_form_task', methods=['POST'])
def add_new_free_form_task():
    if not session.get('username'):
        flash('Vain kirjautuneet käyttäjät voivat lisätä tehtäviä', 'error')
        return redirect('/')

    if not session.get('is_teacher'):
        flash('Vain opettajat voivat lisätä tehtäviä', 'error')
        return redirect('/')
    
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    course_id = request.form['course_id']
    question = request.form['question']
    evaluation_criteria = request.form['evaluation_criteria']
    option_count = request.form['option_count']
    free_form_task_service.create_task(course_id, question, evaluation_criteria)
    return redirect(
        f'/edit_course?course_id={course_id}&option_count={option_count}')


@teacher.route('/view_student_submissions', methods=['POST'])
def view_student_submissions():
    if not session.get("username"):
        flash("Vain kirjautuneet käyttäjät voivat lisätä tehtäviä", "error")
        return redirect("/")

    if not session.get("is_teacher"):
        flash("Vain opettajat voivat lisätä tehtäviä", "error")
        return redirect("/")
    
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    course_id = request.form["course_id"]
    student_id = request.form["student_id"]
    student_username = request.form["student_username"]
    free_form_submissions = free_form_task_service.get_submissions(student_id, course_id)
    multiple_choice_submissions = multiple_choice_task_service.get_submissions(student_id, course_id)

    for submission in multiple_choice_submissions:
        submission["is_correct"] = multiple_choice_task_service.is_correct(submission["submission_id"])

    return render_template(
        "teacher/student_submissions.html",
        course_id=course_id,
        student_id=student_id,
        student_username=student_username,
        free_form_submissions=free_form_submissions,
        multiple_choice_submissions=multiple_choice_submissions,)