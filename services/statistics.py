from sqlalchemy import text
from db import db
from .courses import get_students

def get_course_statistics_by_user_id(user_id, course_id):
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


def get_course_statistics(course_id):
    sql = text("""
              SELECT 'Free Form Task' AS task_type, FT.id AS task_id, FT.question, FS.user_id AS student_id
              FROM student_free_form_task_submissions FS
              JOIN free_form_tasks FT ON FS.task_id = FT.id
              WHERE FT.course_id = :course_id
              UNION
              SELECT 'Multiple Choice Task' AS task_type, MT.id AS task_id, MT.question, MS.user_id AS student_id
              FROM student_multiple_choice_task_submissions MS
              JOIN multiple_choice_tasks MT ON MS.task_id = MT.id
              WHERE MT.course_id = :course_id;
        """)
    result = db.session.execute(sql, {"course_id": course_id})
    rows = result.fetchall()
    submission_count_by_student_id = {}
    for row in rows:
        student_id = row.student_id
        if student_id not in submission_count_by_student_id:
            submission_count_by_student_id[student_id] = {
                "student_id": student_id, "submission_count": 0}
        submission_count_by_student_id[student_id]["submission_count"] += 1
    return list(submission_count_by_student_id.values())


def get_students_with_submissions(course_id):
    students = get_students(course_id)
    students_with_submissions = []

    for student in students:
        id = student.id
        username = student.username
        submissions = get_course_statistics_by_user_id(
            id, course_id)
        students_with_submissions.append(
            {"id": id, "username": username, "submissions": submissions})

    return students_with_submissions