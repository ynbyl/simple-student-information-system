# this file handles all the database queries
# all sql stuff goes here so the controllers dont have to worry about it

import os

import mysql.connector
from dotenv import load_dotenv
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

# load .env so we get the db credentials
load_dotenv(override=True)

bcrypt = Bcrypt()


# ---- User model for flask-login ----

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id            = id
        self.username      = username
        self.password_hash = password_hash

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


def get_user_by_id(user_id):
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM Users WHERE id=%s", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return User(*row) if row else None


def get_user_by_username(username):
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM Users WHERE username=%s", (username,))
    row = cursor.fetchone()
    conn.close()
    return User(*row) if row else None


def username_exists(username):
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Users WHERE username=%s", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def create_user(username, password):
    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Users (username, password) VALUES (%s, %s)",
        (username, hashed),
    )
    conn.commit()
    conn.close()


# helper to connect to the database
def get_db_connection():
    db_config = {
        "host":     os.getenv("DB_HOST", "localhost"),
        "user":     os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "ssis"),
    }
    return mysql.connector.connect(**db_config)


# ---- student queries ----

def get_all_students():
    # get all students from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, first_name, last_name, year_level, gender, coursecode, photo_url "
        "FROM Students"
    )
    students = [
        {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "year_level": row[3],
            "gender": row[4],
            "coursecode": row[5],
            "photo_url": row[6],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return students


def get_student_by_id(student_id):
    # find one student by their id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, first_name, last_name, year_level, gender, coursecode, photo_url "
        "FROM Students WHERE id=%s",
        (student_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "year_level": row[3],
            "gender": row[4],
            "coursecode": row[5],
            "photo_url": row[6],
        }
    return None


def student_id_exists(student_id):
    # check if a student with that id already exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Students WHERE id=%s", (student_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def create_student(student_id, first_name, last_name, year_level, gender, coursecode, photo_url=None):
    # add a new student to the database
    # photo_url is optional, comes from cloudinary
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Students (id, first_name, last_name, year_level, gender, coursecode, photo_url) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (student_id, first_name, last_name, year_level, gender, coursecode, photo_url),
    )
    conn.commit()
    conn.close()


def update_student(student_id, first_name, last_name, year_level, gender, coursecode, photo_url=None):
    # update student info
    # if photo_url is None we dont touch the existing photo
    conn = get_db_connection()
    cursor = conn.cursor()
    if photo_url is None:
        # no new photo uploaded so just update the other fields
        cursor.execute(
            "UPDATE Students "
            "SET first_name=%s, last_name=%s, year_level=%s, gender=%s, coursecode=%s "
            "WHERE id=%s",
            (first_name, last_name, year_level, gender, coursecode, student_id),
        )
    else:
        # new photo was uploaded so update everything including photo
        cursor.execute(
            "UPDATE Students "
            "SET first_name=%s, last_name=%s, year_level=%s, gender=%s, coursecode=%s, photo_url=%s "
            "WHERE id=%s",
            (first_name, last_name, year_level, gender, coursecode, photo_url, student_id),
        )
    conn.commit()
    conn.close()


def delete_student(student_id):
    # delete a student from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Students WHERE id=%s", (student_id,))
    conn.commit()
    conn.close()


def search_students(query):
    # search students by any field, including full name (first + last combined)
    conn = get_db_connection()
    cursor = conn.cursor()
    like = "%" + query.lower() + "%"
    cursor.execute(
        "SELECT id, first_name, last_name, year_level, gender, coursecode, photo_url "
        "FROM Students "
        "WHERE LOWER(id) LIKE %s "
        "   OR LOWER(first_name) LIKE %s "
        "   OR LOWER(last_name) LIKE %s "
        "   OR LOWER(CONCAT(first_name, ' ', last_name)) LIKE %s "
        "   OR LOWER(CONCAT(last_name, ' ', first_name)) LIKE %s "
        "   OR CAST(year_level AS CHAR) LIKE %s "
        "   OR LOWER(gender) LIKE %s "
        "   OR LOWER(coursecode) LIKE %s",
        (like, like, like, like, like, like, like, like),
    )
    results = [
        {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "year_level": row[3],
            "gender": row[4],
            "coursecode": row[5],
            "photo_url": row[6],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return results


# ---- course queries ----

def get_all_courses():
    # get all courses and also include the college name
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT coursecode, coursename, collegecode FROM Courses")
    courses = [
        {"coursecode": row[0], "coursename": row[1], "collegecode": row[2]}
        for row in cursor.fetchall()
    ]

    # make a dictionary so we can match college code to college name
    cursor.execute("SELECT collegecode, collegename FROM Colleges")
    college_map = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()

    for course in courses:
        course["collegename"] = college_map.get(course["collegecode"], "")

    return courses


def get_course_by_code(coursecode):
    # find one course by its code
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT coursecode, coursename, collegecode FROM Courses WHERE coursecode=%s",
        (coursecode,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"coursecode": row[0], "coursename": row[1], "collegecode": row[2]}
    return None


def course_code_exists(coursecode):
    # check if a course with that code already exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT coursecode FROM Courses WHERE coursecode=%s", (coursecode,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def create_course(coursecode, coursename, collegecode):
    # add a new course
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Courses (coursecode, coursename, collegecode) VALUES (%s, %s, %s)",
        (coursecode, coursename, collegecode),
    )
    conn.commit()
    conn.close()


def update_course(coursecode, coursename, collegecode):
    # update a course
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Courses SET coursename=%s, collegecode=%s WHERE coursecode=%s",
        (coursename, collegecode, coursecode),
    )
    conn.commit()
    conn.close()


def delete_course(coursecode):
    # delete a course only if no students are enrolled in it
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Courses WHERE coursecode=%s", (coursecode,))
    conn.commit()
    conn.close()


def course_has_students(coursecode):
    # check if any students are enrolled in this course
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Students WHERE coursecode=%s", (coursecode,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def search_courses(query):
    # search courses by code, name, or college
    conn = get_db_connection()
    cursor = conn.cursor()
    like = "%" + query.lower() + "%"
    cursor.execute(
        "SELECT coursecode, coursename, collegecode FROM Courses "
        "WHERE LOWER(coursecode) LIKE %s "
        "   OR LOWER(coursename) LIKE %s "
        "   OR LOWER(collegecode) LIKE %s",
        (like, like, like),
    )
    results = [
        {"coursecode": row[0], "coursename": row[1], "collegecode": row[2]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return results


# ---- college queries ----

def get_all_colleges():
    # get all colleges
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT collegecode, collegename FROM Colleges")
    colleges = [{"collegecode": row[0], "collegename": row[1]} for row in cursor.fetchall()]
    conn.close()
    return colleges


def get_college_by_code(collegecode):
    # find one college by its code
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT collegecode, collegename FROM Colleges WHERE collegecode=%s",
        (collegecode,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"collegecode": row[0], "collegename": row[1]}
    return None


def college_code_exists(collegecode):
    # check if a college with that code already exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT collegecode FROM Colleges WHERE collegecode=%s", (collegecode,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def create_college(collegecode, collegename):
    # add a new college
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Colleges (collegecode, collegename) VALUES (%s, %s)",
        (collegecode, collegename),
    )
    conn.commit()
    conn.close()


def update_college(collegecode, collegename):
    # update a college name
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Colleges SET collegename=%s WHERE collegecode=%s",
        (collegename, collegecode),
    )
    conn.commit()
    conn.close()


def delete_college(collegecode):
    # delete a college only if it has no courses under it
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Colleges WHERE collegecode=%s", (collegecode,))
    conn.commit()
    conn.close()


def college_has_courses(collegecode):
    # check if any courses belong to this college
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Courses WHERE collegecode=%s", (collegecode,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def search_colleges(query):
    # search colleges by code or name
    conn = get_db_connection()
    cursor = conn.cursor()
    like = "%" + query.lower() + "%"
    cursor.execute(
        "SELECT collegecode, collegename FROM Colleges "
        "WHERE LOWER(collegecode) LIKE %s OR LOWER(collegename) LIKE %s",
        (like, like),
    )
    results = [{"collegecode": row[0], "collegename": row[1]} for row in cursor.fetchall()]
    conn.close()
    return results
