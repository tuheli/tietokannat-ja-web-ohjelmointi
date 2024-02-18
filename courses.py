from sqlalchemy.sql import text
from db import db
from datetime import datetime


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

def add_student_task_answer(user_id, task_id, answer):
    sql = text("""
               INSERT INTO student_task_answers (user_id, task_id, answer) 
               VALUES (:user_id, :task_id, :answer)
               """)
    db.session.execute(sql, {'user_id': user_id, 'task_id': task_id, 'answer': answer})
    db.session.commit()

def get_student_task_answers(user_id, course_id):
    sql = text("""
               SELECT T.id, T.question, STA.answer, STA.task_id
               FROM student_task_answers STA 
               LEFT JOIN tasks T ON STA.task_id = T.id 
               WHERE STA.user_id = :user_id AND T.course_id = :course_id
               """)
    result = db.session.execute(sql, {"user_id": user_id, "course_id": course_id})
    answers = result.fetchall()
    return answers

def add_multiple_choice_task(course_id, question, options):
    task_sql = text(
        """
        INSERT INTO multiple_choice_tasks (course_id, question) 
        VALUES (:course_id, :question)
        RETURNING id
        """
    )
    added_task_id = db.session.execute(task_sql, {"course_id": course_id, "question": question}).fetchone()[0]

    for key in options:
        option_sql = text(
            """
            INSERT INTO multiple_choice_task_options (task_id, option, is_correct) 
            VALUES (:task_id, :option, :is_correct)
            """
        )
        db.session.execute(option_sql, {"task_id": added_task_id, "option": options[key]['text'], "is_correct": options[key]["is_correct"]})
    
    db.session.commit()

def get_multiple_choice_tasks(course_id):
    tasks_sql = text("""
               SELECT id, question 
               FROM multiple_choice_tasks 
               WHERE course_id = :course_id
               """)
    tasks_result = db.session.execute(tasks_sql, {"course_id": course_id})
    tasks_rows = tasks_result.fetchall()

    tasks_dict = {}
    for task_row in tasks_rows:
        id = task_row.id
        question = task_row.question
        tasks_dict[id] = {'question': question, 'options': []}

    for key in tasks_dict:
        options_sql = text("""
                      SELECT option, is_correct 
                      FROM multiple_choice_task_options 
                      WHERE task_id = :task_id
                      """)
        options_result = db.session.execute(options_sql, {"task_id": key})
        options_rows = options_result.fetchall()

        for option_row in options_rows:
            option_text = option_row.option
            is_correct = option_row.is_correct
            tasks_dict[key]['options'].append({'text': option_text, 'is_correct': is_correct})

    return list(tasks_dict.values())

def get_multiple_choice_tasks_without_correct_answers(course_id):
    tasks_sql = text("""
               SELECT id, question 
               FROM multiple_choice_tasks 
               WHERE course_id = :course_id
               """)
    tasks_result = db.session.execute(tasks_sql, {"course_id": course_id})
    tasks_rows = tasks_result.fetchall()

    tasks_dict = {}
    for task_row in tasks_rows:
        id = task_row.id
        question = task_row.question
        tasks_dict[id] = {'question': question, 'options': [], 'id': id}

    for key in tasks_dict:
        options_sql = text("""
                      SELECT id, option 
                      FROM multiple_choice_task_options 
                      WHERE task_id = :task_id
                      """)
        options_result = db.session.execute(options_sql, {"task_id": key})
        options_rows = options_result.fetchall()

        for option_row in options_rows:
            option_text = option_row.option
            option_id = option_row.id
            tasks_dict[key]['options'].append({'text': option_text, 'id': option_id})

    return list(tasks_dict.values())

def add_free_form_task(course_id, question, evaluation_criteria):
    task_sql = text(
        """
        INSERT INTO free_form_tasks (course_id, question, evaluation_criteria) 
        VALUES (:course_id, :question, :evaluation_criteria)
        """
    )
    db.session.execute(task_sql, {"course_id": course_id, "question": question, "evaluation_criteria": evaluation_criteria})
    db.session.commit()

def get_free_form_tasks(course_id):
    sql = text("""
               SELECT id, question, evaluation_criteria 
               FROM free_form_tasks 
               WHERE course_id = :course_id
               """)
    result = db.session.execute(sql, {"course_id": course_id})
    task_rows = result.fetchall()
    return task_rows

def get_free_form_tasks_without_evaluation_criteria(course_id):
    sql = text("""
               SELECT id, question 
               FROM free_form_tasks 
               WHERE course_id = :course_id
               """)
    result = db.session.execute(sql, {"course_id": course_id})
    task_rows = result.fetchall()
    return task_rows

def add_free_form_task_submission(user_id, task_id, answer):
    submission_sql = text("""
            INSERT INTO student_free_form_task_submissions (user_id, task_id, submission_time) 
            VALUES (:user_id, :task_id, :submission_time)
            RETURNING id
            """)
    submission_id = db.session.execute(submission_sql, {"user_id": user_id, "task_id": task_id, "submission_time": datetime.now()}).fetchone()[0]

    answer_sql = text("""
               INSERT INTO student_free_form_task_answers (user_id, task_id, submission_id, answer) 
               VALUES (:user_id, :task_id, :submission_id, :answer)
               """)
    db.session.execute(answer_sql, {'user_id': user_id, 'task_id': task_id, 'submission_id': submission_id ,'answer': answer})
    db.session.commit()

def add_multiple_choice_task_submission(user_id, task_id, selected_options):
    submission_sql = text("""
            INSERT INTO student_multiple_choice_task_submissions (user_id, task_id, submission_time) 
            VALUES (:user_id, :task_id, :submission_time)
            RETURNING id
            """)
    submission_id = db.session.execute(submission_sql, {"user_id": user_id, "task_id": task_id, "submission_time": datetime.now()}).fetchone()[0]

    for option_id in selected_options:
        answer_sql = text("""
               INSERT INTO student_multiple_choice_task_answers (user_id, task_id, submission_id, option_id, students_choice) 
               VALUES (:user_id, :task_id, :submission_id, :option_id, :students_choice)
               """)
        db.session.execute(answer_sql, {'user_id': user_id, 'task_id': task_id, 'submission_id': submission_id, 'option_id': option_id, 'students_choice': selected_options[option_id]['students_choice']})
    db.session.commit()

def get_students_multiple_choice_task_answers(user_id, course_id):
    sql = text("""
               SELECT T.id AS task_id , T.question, S.submission_time, A.option_id, A.students_choice, S.id AS submission_id, O.option
               FROM student_multiple_choice_task_submissions S
               LEFT JOIN multiple_choice_tasks T ON S.task_id = T.id
               LEFT JOIN student_multiple_choice_task_answers A ON S.id = A.submission_id
               LEFT JOIN multiple_choice_task_options O ON A.option_id = O.id
               WHERE S.user_id = :user_id AND T.course_id = :course_id
               ORDER BY T.id ASC
               """)
    result = db.session.execute(sql, {"user_id": user_id, "course_id": course_id})
    students_choices = result.fetchall()
    return students_choices

def get_free_form_task_submissions(user_id, course_id):
    sql = text("""
               SELECT T.id AS task_id , T.question, S.submission_time, A.answer, S.id AS submission_id
               FROM student_free_form_task_submissions S
               LEFT JOIN free_form_tasks T ON S.task_id = T.id
               LEFT JOIN student_free_form_task_answers A ON S.id = A.submission_id
               WHERE S.user_id = :user_id AND T.course_id = :course_id
               ORDER BY T.id ASC
               """)
    result = db.session.execute(sql, {"user_id": user_id, "course_id": course_id})
    submissions = result.fetchall()
    return submissions

def parse_multiple_choice_task_options(request):
    options = {}
    for key in request.form.keys():
        if key.startswith('options'):
            option_id_start = key.find('[') + 1
            option_id_end = key.find(']', option_id_start)
            option_id = int(key[option_id_start:option_id_end])
            if option_id not in options:
                options[option_id] = {'text': '', 'is_correct': False}
            if 'text' in key:
                options[option_id]['text'] = request.form[key]
            elif 'is_correct' in key:
                options[option_id]['is_correct'] = True
    return options

def parse_multiple_choice_task_submission(request):
    form_keys = request.form.keys()
    selected_options = {}
    for key in form_keys:
        if key.startswith('selected_options'):
            option_id_start = key.find('[') + 1
            option_id_end = key.find(']', option_id_start)
            option_id = int(key[option_id_start:option_id_end])
            if option_id not in selected_options:
                selected_options[option_id] = {'students_choice': True}

    all_options = {}
    for key in form_keys:
        if key.startswith('all_options'):
            option_id_start = key.find('[') + 1
            option_id_end = key.find(']', option_id_start)
            option_id = int(key[option_id_start:option_id_end])
            if option_id not in all_options:
                all_options[option_id] = 1

    for key in all_options:
        if key not in selected_options:
            selected_options[key] = {'students_choice': False}

    return selected_options

def students_multiple_choice_answers_to_submissions(answer_rows):
    submissions_dict = {}
    for answer_row in answer_rows:
        task_id = answer_row.task_id
        question = answer_row.question
        submission_time = answer_row.submission_time
        submission_id = answer_row.submission_id
        option_id = answer_row.option_id
        option_text = answer_row.option
        students_choice = answer_row.students_choice
        if submission_id not in submissions_dict:
            submissions_dict[submission_id] = {'submission_id': submission_id, 'submission_time': submission_time, 'task_id': task_id ,'question': question, 'options': []}
        submissions_dict[submission_id]['options'].append({'id': option_id, 'students_choice': students_choice, 'text': option_text})
    return list(submissions_dict.values())
        