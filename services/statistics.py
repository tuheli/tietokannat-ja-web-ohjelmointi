from sqlalchemy import text
from db import db

def get_submission_statistics(user_id, course_id):
    sql = text("""
              SELECT 'Free Form Task' AS task_type, FT.id AS task_id, FT.question, FS.user_id AS student_id
              FROM student_free_form_task_submissions FS
              JOIN free_form_tasks FT ON FS.task_id = FT.id
              WHERE FS.user_id = :user_id AND FT.course_id = :course_id
              UNION
              SELECT 'Multiple Choice Task' AS task_type, MT.id AS task_id, MT.question, MS.user_id AS student_id
              FROM student_multiple_choice_task_submissions MS
              JOIN multiple_choice_tasks MT ON MS.task_id = MT.id
              WHERE MS.user_id = :user_id AND MT.course_id = :course_id;
        """)
    result = db.session.execute(sql, {"user_id": user_id, "course_id": course_id})
    submissions = result.fetchall()
    return submissions