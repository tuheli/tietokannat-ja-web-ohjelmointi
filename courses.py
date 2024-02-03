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