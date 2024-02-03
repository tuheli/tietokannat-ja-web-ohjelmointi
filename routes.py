from app import app
from flask import flash, redirect, render_template, request, session
from courses import get_course, get_joined_courses, get_available_courses, get_materials, is_valid_new_course, update_materials
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
    
    sql_course = text("INSERT INTO courses (title, description) VALUES (:title, :description) RETURNING id")
    sql_user_courses = text("INSERT INTO user_courses (user_id, course_id) VALUES (:user_id, :course_id)")

    result = db.session.execute(sql_course, {"title": title, "description": description })
    db.session.execute(sql_user_courses, {"user_id": session.get("user_id"), "course_id": result.fetchone()[0] })
    db.session.commit()

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
    materials = get_materials(course_id)
    return render_template('edit_course.html', course=course, materials=materials)

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