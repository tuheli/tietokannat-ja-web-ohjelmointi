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