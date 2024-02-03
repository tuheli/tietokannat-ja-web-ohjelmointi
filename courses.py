from sqlalchemy.sql import text
from db import db


def is_valid_new_course(title, description):
    if not title or len(title) > 255:
        return False
    if not description or len(description) > 1000:
        return False
    return True

def get_joined_courses(user_id):
    sql = text("""
               SELECT C.id, C.title, C.description 
               FROM courses C 
               LEFT JOIN user_courses UC ON C.id = UC.course_id 
               WHERE UC.user_id = :user_id
               """)
    result = db.session.execute(sql, {"user_id": user_id})
    courses = result.fetchall()
    return courses

def get_available_courses(user_id):
    sql = text("""
               SELECT C.id, C.title, C.description 
               FROM courses C 
               LEFT JOIN user_courses UC ON C.id = UC.course_id AND UC.user_id = :user_id 
               WHERE UC.user_id IS NULL
               """)
    result = db.session.execute(sql, {"user_id": user_id})
    courses = result.fetchall()
    return courses

def get_course(course_id):
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