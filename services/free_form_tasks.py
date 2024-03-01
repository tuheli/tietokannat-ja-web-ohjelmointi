from datetime import datetime
from sqlalchemy import text
from app import db


def create_task(course_id, question, evaluation_criteria):
    task_sql = text(
        """
        INSERT INTO free_form_tasks (course_id, question, evaluation_criteria)
        VALUES (:course_id, :question, :evaluation_criteria)
        """
    )
    db.session.execute(task_sql,
                       {"course_id": course_id,
                        "question": question,
                        "evaluation_criteria": evaluation_criteria})
    db.session.commit()


def create_submission(user_id, task_id, answer):
    submission_sql = text("""
            INSERT INTO student_free_form_task_submissions (user_id, task_id, submission_time)
            VALUES (:user_id, :task_id, :submission_time)
            RETURNING id
            """)
    submission_id = db.session.execute(
        submission_sql, {
            "user_id": user_id, "task_id": task_id, "submission_time": datetime.now()}).fetchone()[0]

    answer_sql = text("""
               INSERT INTO student_free_form_task_answers (user_id, task_id, submission_id, answer)
               VALUES (:user_id, :task_id, :submission_id, :answer)
               """)
    db.session.execute(answer_sql,
                       {'user_id': user_id,
                        'task_id': task_id,
                        'submission_id': submission_id,
                        'answer': answer})
    db.session.commit()


def get(course_id):
    sql = text("""
               SELECT id, question, evaluation_criteria
               FROM free_form_tasks
               WHERE course_id = :course_id
               """)
    result = db.session.execute(sql, {"course_id": course_id})
    task_rows = result.fetchall()
    return task_rows


def get_without_evaluation_criteria(course_id):
    sql = text("""
               SELECT id, question
               FROM free_form_tasks
               WHERE course_id = :course_id
               """)
    result = db.session.execute(sql, {"course_id": course_id})
    task_rows = result.fetchall()
    return task_rows


def get_submissions(user_id, course_id):
    sql = text("""
               SELECT T.id AS task_id , T.question, S.submission_time, A.answer, S.id AS submission_id
               FROM student_free_form_task_submissions S
               LEFT JOIN free_form_tasks T ON S.task_id = T.id
               LEFT JOIN student_free_form_task_answers A ON S.id = A.submission_id
               WHERE S.user_id = :user_id AND T.course_id = :course_id
               ORDER BY T.id ASC
               """)
    result = db.session.execute(
        sql, {"user_id": user_id, "course_id": course_id})
    submissions = result.fetchall()
    return submissions

