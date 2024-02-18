CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_teacher BOOLEAN NOT NULL
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE user_courses (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, course_id)
);

CREATE TABLE course_materials (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE UNIQUE,
    content TEXT NOT NULL
);

-- CREATE TABLE tasks (
--     id SERIAL PRIMARY KEY,
--     course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
--     question TEXT NOT NULL,
--     answer_type VARCHAR(50) NOT NULL
-- );

-- CREATE TABLE task_answers (
--     id SERIAL PRIMARY KEY,
--     task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
--     answer TEXT NOT NULL
-- );

CREATE TABLE free_form_tasks (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    evaluation_criteria TEXT NOT NULL
);

CREATE TABLE multiple_choice_tasks (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    question TEXT NOT NULL
);

CREATE TABLE multiple_choice_task_options (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES multiple_choice_tasks(id) ON DELETE CASCADE,
    option TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL
);

CREATE TABLE student_free_form_task_submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES free_form_tasks(id) ON DELETE CASCADE,
    submission_time TIMESTAMP NOT NULL
);

CREATE TABLE student_free_form_task_answers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES free_form_tasks(id) ON DELETE CASCADE,
    submission_id INTEGER REFERENCES student_free_form_task_submissions(id) ON DELETE CASCADE,
    answer TEXT NOT NULL
);

CREATE TABLE student_multiple_choice_task_answers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES multiple_choice_tasks(id) ON DELETE CASCADE,
    option_id INTEGER REFERENCES multiple_choice_task_options(id) ON DELETE CASCADE,
    submission_id INTEGER REFERENCES student_multiple_choice_task_submissions(id) ON DELETE CASCADE,
    students_choice BOOLEAN NOT NULL
);

CREATE TABLE student_multiple_choice_task_submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES multiple_choice_tasks(id) ON DELETE CASCADE,
    submission_time TIMESTAMP NOT NULL
);

SELECT * FROM student_free_form_task_submissions;
SELECT * FROM student_free_form_task_answers;
DROP TABLE IF EXISTS student_task_answers;
DROP TABLE IF EXISTS student_multiple_choice_task_answers;