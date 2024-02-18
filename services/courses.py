from sqlalchemy import text
from app import db


def create(user_id, title, description):
    sql_course = text(
        """
        INSERT INTO courses (title, description)
        VALUES (:title, :description)
        RETURNING id
        """
    )

    sql_user_courses = text(
        """
        INSERT INTO user_courses (user_id, course_id)
        VALUES (:user_id, :course_id)
        """
    )

    course_result = db.session.execute(
        sql_course, {"title": title, "description": description})

    added_course_id = course_result.fetchone()[0]

    db.session.execute(
        sql_user_courses, {
            "user_id": user_id, "course_id": added_course_id})
    db.session.commit()


def get_users_courses(user_id):
    sql = text("""
               SELECT C.id, C.title, C.description
               FROM courses C
               LEFT JOIN user_courses UC ON C.id = UC.course_id
               WHERE UC.user_id = :user_id
               """)
    result = db.session.execute(sql, {"user_id": user_id})
    courses = result.fetchall()
    return courses


def get_joinable_courses(user_id):
    sql = text("""
               SELECT C.id, C.title, C.description
               FROM courses C
               LEFT JOIN user_courses UC ON C.id = UC.course_id AND UC.user_id = :user_id
               WHERE UC.user_id IS NULL
               """)
    result = db.session.execute(sql, {"user_id": user_id})
    courses = result.fetchall()
    return courses


def get_materials(course_id):
    sql = text("""
               SELECT content
               FROM course_materials
               WHERE course_id = :course_id
               """)
    result = db.session.execute(sql, {"course_id": course_id})
    materials = result.fetchone()
    if not materials:
        return "Kurssilla ei ole materiaalia."
    return materials[0]


def get_students(course_id):
    sql = text("""
               SELECT U.id, U.username
               FROM users U
               LEFT JOIN user_courses UC ON U.id = UC.user_id
               WHERE UC.course_id = :course_id AND U.is_teacher = FALSE
               """)
    result = db.session.execute(sql, {"course_id": course_id})
    students = result.fetchall()
    return students


def get(course_id):
    sql = text("""
               SELECT id, title, description
               FROM courses
               WHERE id = :id
               """)
    result = db.session.execute(sql, {"id": course_id})
    course = result.fetchone()
    return course


def update_materials(course_id, content):
    sql = text("""
               INSERT INTO course_materials (course_id, content)
               VALUES (:course_id, :content)
               ON CONFLICT (course_id)
               DO UPDATE SET content = EXCLUDED.content;
               """)
    db.session.execute(sql, {"course_id": course_id, "content": content})
    db.session.commit()


def update_title(course_id, new_title):
    if not new_title or len(new_title) > 255:
        return False

    sql = text("""
               UPDATE courses
               SET title = :new_name
               WHERE id = :course_id
               """)
    db.session.execute(sql, {"new_name": new_title, "course_id": course_id})
    db.session.commit()
    return True


def delete(course_id):
    sql = text("""
               DELETE FROM courses
               WHERE id = :course_id
               """
               )
    db.session.execute(sql, {"course_id": course_id})
    db.session.commit()


def is_valid_course(title, description):
    if not title or len(title) > 255:
        return False
    if not description or len(description) > 1000:
        return False
    return True