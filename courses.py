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

def get_course_materials(course_id):
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

def add_course(user_id, title, description):
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

    course_result = db.session.execute(sql_course, {"title": title, "description": description })

    added_course_id = course_result.fetchone()[0]

    db.session.execute(sql_user_courses, {"user_id": user_id, "course_id": added_course_id })
    db.session.commit()

def add_task(course_id, question, answer_type, answer):
    task_sql = text(
        """
        INSERT INTO tasks (course_id, question, answer_type) 
        VALUES (:course_id, :question, :answer_type)
        RETURNING id
        """
    )

    answer_sql = text(
        """
        INSERT INTO task_answers (task_id, answer) 
        VALUES (:task_id, :answer)
        """
    )

    task_result = db.session.execute(task_sql, {"course_id": course_id, "question": question, "answer_type": answer_type})
    
    added_task_id = task_result.fetchone()[0]

    db.session.execute(answer_sql, {"task_id": added_task_id, "answer": answer})
    db.session.commit()

def get_tasks(course_id):
    sql = text("""
               SELECT id, question, answer_type 
               FROM tasks T
               WHERE course_id = :course_id
               """)
    result = db.session.execute(sql, {"course_id": course_id})
    tasks = result.fetchall()
    return tasks

def get_answers(course_id):
    sql = text(
        """
        SELECT TA.task_id, TA.answer
        FROM task_answers TA
        LEFT JOIN tasks T ON TA.task_id = T.id
        WHERE T.course_id = :course_id
        """
    )
    result = db.session.execute(sql, {"course_id": course_id})
    answers = result.fetchall()
    return answers

def delete_course_by_id(course_id):
    sql = text("""
               DELETE FROM courses 
               WHERE id = :course_id
               """
    )
    db.session.execute(sql, {"course_id": course_id})
    db.session.commit()

def update_course(course_id, new_title):
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

def get_course_students(course_id):
    sql = text("""
               SELECT U.id, U.username 
               FROM users U 
               LEFT JOIN user_courses UC ON U.id = UC.user_id 
               WHERE UC.course_id = :course_id AND U.is_teacher = FALSE
               """)
    result = db.session.execute(sql, {"course_id": course_id})
    students = result.fetchall()
    return students