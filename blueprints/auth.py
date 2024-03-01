import secrets
from flask import Blueprint, redirect, render_template, request, session, flash
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from app import db

auth = Blueprint("auth", __name__)


@auth.route("/logout")
def logout():
    del session["username"]
    return redirect("/")


@auth.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if not username:
        flash("Käyttäjätunnus puuttuu", "error")
        return redirect("/")
    
    if not password:
        flash("Salasana puuttuu", "error")
        return render_template("auth/login.html", username=username)

    sql = text(
        "SELECT id, password_hash, is_teacher FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    if not user:
        flash('Käyttäjätunnus ei kelpaa', 'error')
        return render_template("auth/login.html", username=username)
    else:
        hash_value = user.password_hash
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["is_teacher"] = user.is_teacher
            session["user_id"] = user.id
            session["csrf_token"] = secrets.token_hex(16)

            flash('Onnistunut kirjautuminen', 'success')
            return redirect("/")
        else:
            flash('Salasana ei kelpaa', 'error')
            return render_template("auth/login.html", username=username)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        is_teacher = 'is_teacher' in request.form

        if (len(username) < 4 or len(username) > 16):
            flash('Käyttäjätunnuksen pituus on oltava 4-16 merkkiä', 'error')
            return render_template("auth/register.html", username=username, is_teacher=is_teacher)

        if (len(password) < 4 or len(password) > 128):
            flash('Salasanan pituus on oltava 4-128 merkkiä', 'error')
            return render_template("auth/register.html", username=username, is_teacher=is_teacher)

        sql = text("SELECT id FROM users WHERE username=:username")
        result = db.session.execute(sql, {"username": username})
        user = result.fetchone()

        if user:
            flash('Tunnus on jo käytössä', 'error')
            return render_template("auth/register.html", username=username, is_teacher=is_teacher)
        else:
            hash_value = generate_password_hash(password)

            sql = text(
                "INSERT INTO users (username, password_hash, is_teacher) VALUES (:username, :password_hash, :is_teacher)")
            db.session.execute(sql,
                               {"username": username,
                                "password_hash": hash_value,
                                "is_teacher": is_teacher})
            db.session.commit()

            flash('Tunnuksen luonti onnistui', 'success')
            return redirect("/")
    else:
        return render_template("auth/register.html")
