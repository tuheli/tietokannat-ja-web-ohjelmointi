from app import app
from flask import flash, redirect, render_template, request, session
from courses import add_course, add_task, delete_course_by_id, get_course, get_answers, get_course_students, get_joined_courses, get_available_courses, get_course_materials, get_tasks, is_valid_new_course, update_course, update_materials
from db import db
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash


@app.route("/")
def index():
    if "username" not in session:
        return render_template("index.html")
    
    user_id = session.get("user_id")
    joined_courses = get_joined_courses(user_id)

    if session.get('is_teacher'):
        return render_template("teacher_dashboard.html", courses=joined_courses)
    else:
        available_courses = get_available_courses(user_id)
        return render_template("student_dashboard.html", joined_courses=joined_courses, available_courses=available_courses)

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql = text("SELECT id, password_hash, is_teacher FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()

    if not user:
        flash('Käyttäjätunnus ei kelpaa', 'error')
        return redirect("/")
    else:
        hash_value = user.password_hash
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["is_teacher"] = user.is_teacher
            session["user_id"] = user.id
            flash('Onnistunut kirjautuminen', 'success')
            return redirect("/")
        else:
            flash('Salasana ei kelpaa', 'error')
            return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        is_teacher = 'is_teacher' in request.form

        if (len(username) < 4 or len(username) > 16):
            flash('Käyttäjätunnuksen pituus on oltava 4-16 merkkiä', 'error')
            return redirect("/register")
        
        if (len(password) < 4 or len(password) > 128):
            flash('Salasanan pituus on oltava 4-128 merkkiä', 'error')
            return redirect("/register")

        sql = text("SELECT id FROM users WHERE username=:username")
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()

        if user:
            flash('Tunnus on jo käytössä', 'error')
            return redirect("/register")
        else:
            hash_value = generate_password_hash(password)

            sql = text("INSERT INTO users (username, password_hash, is_teacher) VALUES (:username, :password_hash, :is_teacher)")
            db.session.execute(sql, {"username": username, "password_hash": hash_value, "is_teacher": is_teacher})
            db.session.commit()

            flash('Tunnuksen luonti onnistui', 'success')
            return redirect("/")
    else:
        return render_template("register.html")
    
@app.route('/create_course', methods=['POST'])
def create_course():
    if not session.get('is_teacher'):
        flash('Vain opettajat voivat luoda kursseja', 'error')
        return redirect('/')
    
    title = request.form['title']
    description = request.form['description']

    if not is_valid_new_course(title, description):
        flash('Kurssin tiedot eivät kelpaa', 'error')
        return redirect('/')

    add_course(session.get('user_id'), title, description)
    flash('Kurssin luonti onnistui', 'success')
    return redirect('/')

@app.route('/join_course', methods=['POST'])
def join_course():
    course_id = request.form['course_id']
    sql = text("INSERT INTO user_courses (user_id, course_id) VALUES (:user_id, :course_id)")
    db.session.execute(sql, {"user_id": session.get("user_id"), "course_id": course_id})
    db.session.commit()
    return redirect('/')

@app.route('/edit_course', methods=['GET'])
def edit_course():
    if not session.get('is_teacher'):
        flash('Vain opettajat voivat muokata kursseja', 'error')
        return redirect('/')
    
    course_id = request.args.get('course_id')
    course = get_course(course_id)
    materials = get_course_materials(course_id)
    tasks = get_tasks(course_id)
    answers = get_answers(course_id)
    students = get_course_students(course_id)

    # Nyt haetaan erikseen koko kurssin tehtävät ja vastaukset ja liitetään ne yhteen.

    tasks_with_answers = {}
    for task in tasks:
        if task.id not in tasks_with_answers:
            tasks_with_answers[task.id] = {
                "task_id": task.id, 
                "question": task.question, 
                "answer_type": task.answer_type, 
                "answers": []}
        for answer in answers:
            if answer.task_id == task.id:
                tasks_with_answers[task.id]["answers"].append(answer.answer)

    tasks_with_answers_list = list(tasks_with_answers.values())
    return render_template('edit_course.html', course=course, materials=materials, tasks=tasks_with_answers_list, students=students)

@app.route('/update_course_materials', methods=['POST'])
def update_course_materials():
    if not session.get('is_teacher'):
        flash('Vain opettajat voivat muokata kursseja', 'error')
        return redirect('/')
    
    course_id = request.form['course_id']
    materials = request.form['materials']

    update_materials(course_id, materials)
    flash('Kurssimateriaali päivitetty onnistuneesti.', 'success')
    return redirect(f'/edit_course?course_id={course_id}')

@app.route('/add_course_task', methods=['POST'])
def add_course_task():
    if not session.get('is_teacher'):
        flash('Vain opettajat voivat lisätä tehtäviä', 'error')
        return redirect('/')
    
    course_id = request.form['course_id']
    question = request.form['question']
    answer_type = request.form['answer_type']
    task_answer = request.form['task_answer']

    if answer_type != "multiple_choice_answer" and answer_type != "open_answer":
        flash('Vastauksen tyyppi ei kelpaa', 'error')
        return redirect(f'/edit_course?course_id={course_id}')

    add_task(course_id, question, answer_type, task_answer)
    return redirect(f'/edit_course?course_id={course_id}')

@app.route('/student_course_page', methods=['GET'])
def student_course_page():
    course_id = request.args.get('course_id')
    course = get_course(course_id)
    materials = get_course_materials(course_id)
    tasks = get_tasks(course_id)

    return render_template('student_course_page.html', course=course, materials=materials, tasks=tasks)

@app.route('/delete_course', methods=['POST'])
def delete_course():
    if not session.get('is_teacher'):
        flash('Vain opettajat voivat poistaa kursseja', 'error')
        return redirect('/')

    course_id = request.form['course_id']
    delete_course_by_id(course_id)
    return redirect('/')

@app.route('/update_course_title', methods=['POST'])
def update_course_title():
    if not session.get('is_teacher'):
        flash('Vain opettajat voivat muokata kursseja', 'error')
        return redirect('/')

    course_id = request.form['course_id']
    new_title = request.form['new_title']

    was_update_successful = update_course(course_id, new_title)
    
    if was_update_successful:
        flash('Kurssin nimi päivitettiin onnistuneesti', 'success')
        return redirect(f'/edit_course?course_id={course_id}')
    else:
        flash('Kurssin nimen päivitys epäonnistui. Nimen tulee olla määritelty ja se saa olla enintään 255 merkkiä pitkä.', 'error')
        return redirect(f'/edit_course?course_id={course_id}')

