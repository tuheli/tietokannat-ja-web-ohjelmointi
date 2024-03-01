from datetime import datetime
from sqlalchemy import text
from app import db


def create_task(course_id, question, options):
    task_sql = text(
        """
        INSERT INTO multiple_choice_tasks (course_id, question)
        VALUES (:course_id, :question)
        RETURNING id
        """
    )
    added_task_id = db.session.execute(
        task_sql, {"course_id": course_id, "question": question}).fetchone()[0]

    for key in options:
        option_sql = text(
            """
            INSERT INTO multiple_choice_task_options (task_id, option, is_correct)
            VALUES (:task_id, :option, :is_correct)
            """
        )
        db.session.execute(option_sql,
                           {"task_id": added_task_id,
                            "option": options[key]['text'],
                               "is_correct": options[key]["is_correct"]})

    db.session.commit()


def create_submission(user_id, task_id, selected_options):
    submission_sql = text("""
            INSERT INTO student_multiple_choice_task_submissions (user_id, task_id, submission_time)
            VALUES (:user_id, :task_id, :submission_time)
            RETURNING id
            """)
    submission_id = db.session.execute(
        submission_sql, {
            "user_id": user_id, "task_id": task_id, "submission_time": datetime.now()}).fetchone()[0]

    for option_id in selected_options:
        answer_sql = text("""
               INSERT INTO student_multiple_choice_task_answers (user_id, task_id, submission_id, option_id, students_choice)
               VALUES (:user_id, :task_id, :submission_id, :option_id, :students_choice)
               """)
        db.session.execute(answer_sql,
                           {'user_id': user_id,
                            'task_id': task_id,
                            'submission_id': submission_id,
                            'option_id': option_id,
                            'students_choice': selected_options[option_id]['students_choice']})
    db.session.commit()


def get(course_id):
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
            tasks_dict[key]['options'].append(
                {'text': option_text, 'is_correct': is_correct})

    return list(tasks_dict.values())


def get_without_answers(course_id):
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
            tasks_dict[key]['options'].append(
                {'text': option_text, 'id': option_id})

    return list(tasks_dict.values())


def get_submissions(user_id, course_id):
    sql = text("""
               SELECT T.id AS task_id , T.question, S.submission_time, A.option_id, A.students_choice, S.id AS submission_id, O.option
               FROM student_multiple_choice_task_submissions S
               LEFT JOIN multiple_choice_tasks T ON S.task_id = T.id
               LEFT JOIN student_multiple_choice_task_answers A ON S.id = A.submission_id
               LEFT JOIN multiple_choice_task_options O ON A.option_id = O.id
               WHERE S.user_id = :user_id AND T.course_id = :course_id
               ORDER BY T.id ASC
               """)
    rows = db.session.execute(
        sql, {"user_id": user_id, "course_id": course_id}).fetchall()
    submissions = parse_answers(rows)
    return submissions


def parse_options(request):
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


def parse_submission(request):
    def get_option_id(key):
        option_id_start = key.find('[') + 1
        option_id_end = key.find(']', option_id_start)
        return int(key[option_id_start:option_id_end])

    form_keys = request.form.keys()
    selected_options = {}
    all_options = {}

    for key in form_keys:
        if key.startswith('selected_options'):
            option_id = get_option_id(key)
            selected_options[option_id] = {'students_choice': True}
        elif key.startswith('all_options'):
            option_id = get_option_id(key)
            all_options[option_id] = 1

    for key in all_options:
        if key not in selected_options:
            selected_options[key] = {'students_choice': False}

    return selected_options


def parse_answers(answer_rows):
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
            submissions_dict[submission_id] = {
                'submission_id': submission_id,
                'submission_time': submission_time,
                'task_id': task_id,
                'question': question,
                'options': []}
        submissions_dict[submission_id]['options'].append(
            {'id': option_id, 'students_choice': students_choice, 'text': option_text})
    return list(submissions_dict.values())