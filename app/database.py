# this script creates the database and tables
# run this first before running the app
# python app/database.py

import os
import random

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

DATABASE_NAME = os.getenv("DB_NAME", "ssis")

cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
cursor.execute(f"USE {DATABASE_NAME}")

# drop in order because of foreign keys
cursor.execute("DROP TABLE IF EXISTS Students")
cursor.execute("DROP TABLE IF EXISTS Courses")
cursor.execute("DROP TABLE IF EXISTS Colleges")
cursor.execute("DROP TABLE IF EXISTS Users")

cursor.execute(
    """
    CREATE TABLE Users (
        id       INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(150) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    )
    """
)

cursor.execute(
    """
    CREATE TABLE Colleges (
        collegecode VARCHAR(255) PRIMARY KEY,
        collegename VARCHAR(255) NOT NULL
    )
    """
)

cursor.execute(
    """
    CREATE TABLE Courses (
        coursecode  VARCHAR(255) PRIMARY KEY,
        coursename  VARCHAR(255) NOT NULL,
        collegecode VARCHAR(255),
        FOREIGN KEY (collegecode) REFERENCES Colleges(collegecode)
    )
    """
)

cursor.execute(
    """
    CREATE TABLE Students (
        id          VARCHAR(255) PRIMARY KEY,
        first_name  VARCHAR(255) NOT NULL,
        last_name   VARCHAR(255) NOT NULL,
        year_level  INT          NOT NULL,
        gender      VARCHAR(255) NOT NULL,
        coursecode  VARCHAR(255),
        photo_url   VARCHAR(500),
        FOREIGN KEY (coursecode) REFERENCES Courses(coursecode)
    )
    """
)

connection.commit()
connection.close()

print(f"Database '{DATABASE_NAME}' and tables created successfully.")


# ── Seed Data ────────────────────────────────────────────────────────────────

connection = mysql.connector.connect(**{**db_config, "database": DATABASE_NAME})
cursor = connection.cursor()

# ── Colleges ─────────────────────────────────────────────────────────────────
colleges = [
    ("CASS", "College of Arts and Social Sciences"),
    ("CCS",  "College of Computer Studies"),
    ("CSM",  "College of Science and Mathematics"),
    ("CED",  "College of Education"),
    ("CEBA", "College of Economics, Business and Accountancy"),
    ("COE",  "College of Engineering"),
]
cursor.executemany(
    "INSERT IGNORE INTO Colleges (collegecode, collegename) VALUES (%s, %s)",
    colleges,
)

# ── Courses ───────────────────────────────────────────────────────────────────
courses = [
    ("BAENG",  "Bachelor of Arts in English",                       "CASS"),
    ("BAFIL",  "Bachelor of Arts in Filipino",                      "CASS"),
    ("BAHIS",  "Bachelor of Arts in History",                       "CASS"),
    ("BAPOL",  "Bachelor of Arts in Political Science",             "CASS"),
    ("BSPSY",  "Bachelor of Science in Psychology",                 "CASS"),
    ("BAPHI",  "Bachelor of Arts in Philosophy",                    "CASS"),
    ("BSCS",   "Bachelor of Science in Computer Science",           "CCS"),
    ("BSIT",   "Bachelor of Science in Information Technology",     "CCS"),
    ("BSIS",   "Bachelor of Science in Information Systems",        "CCS"),
    ("BSCA",   "Bachelor of Science in Computer Applications",      "CCS"),
    ("BSBIO",  "Bachelor of Science in Biology",                    "CSM"),
    ("BSCHEM", "Bachelor of Science in Chemistry",                  "CSM"),
    ("BSMATH", "Bachelor of Science in Mathematics",                "CSM"),
    ("BSPHY",  "Bachelor of Science in Physics",                    "CSM"),
    ("BSSTAT", "Bachelor of Science in Statistics",                 "CSM"),
    ("BSSE",   "Bachelor of Science in Science Education",          "CED"),
    ("BSED",   "Bachelor of Secondary Education",                   "CED"),
    ("BEED",   "Bachelor of Elementary Education",                  "CED"),
    ("BTLED",  "Bachelor of Technology and Livelihood Education",   "CED"),
    ("BPE",    "Bachelor of Physical Education",                    "CED"),
    ("BSA",    "Bachelor of Science in Accountancy",                "CEBA"),
    ("BSBA",   "Bachelor of Science in Business Administration",    "CEBA"),
    ("BSECON", "Bachelor of Science in Economics",                  "CEBA"),
    ("BSENT",  "Bachelor of Science in Entrepreneurship",           "CEBA"),
    ("BSHM",   "Bachelor of Science in Hospitality Management",     "CEBA"),
    ("BSMM",   "Bachelor of Science in Marketing Management",       "CEBA"),
    ("BSCE",   "Bachelor of Science in Civil Engineering",          "COE"),
    ("BSCpE",  "Bachelor of Science in Computer Engineering",       "COE"),
    ("BSEE",   "Bachelor of Science in Electrical Engineering",     "COE"),
    ("BSECE",  "Bachelor of Science in Electronics Engineering",    "COE"),
    ("BSME",   "Bachelor of Science in Mechanical Engineering",     "COE"),
]
cursor.executemany(
    "INSERT IGNORE INTO Courses (coursecode, coursename, collegecode) VALUES (%s, %s, %s)",
    courses,
)

# ── Students ──────────────────────────────────────────────────────────────────
first_names_male = [
    "John", "Joshua", "Christian", "Mark", "John Mark", "Jerome",
    "Jayson", "Ryan", "Kevin", "Kenneth", "Bryan", "Michael",
    "Daniel", "Adrian", "Nathan", "Paolo", "Carlo", "Juan Carlo",
    "John Paul", "Prince", "Patrick", "Renz", "Carl", "Angelo",
    "Gabriel", "Sean", "Ethan", "Kyle", "Jomar", "Ralph",
    "James", "Reymart", "Jerico", "Von", "Ace", "Cedric",
    "Lester", "Jude", "Miguel", "Vincent",
]
first_names_female = [
    "Mary Grace", "Angel", "Angela", "Joy", "Rose", "Mae",
    "Princess", "Janelle", "Nicole", "Hannah", "Patricia", "Kimberly",
    "Camille", "Abigail", "Jasmine", "Christine", "Kristine", "Jenny",
    "Joanna", "Alyssa", "Andrea", "Samantha", "Kate", "Bianca",
    "Faith", "Rica", "Mika", "Trisha", "Rachelle", "Mae Ann",
    "Charlene", "Marielle", "Frances", "Danica", "Sheena", "Katrina",
    "Ella", "Sophia", "Maria", "Angelica",
]
last_names = [
    "Dela Cruz", "Santos", "Reyes", "Garcia", "Mendoza",
    "Torres", "Ramos", "Flores", "Aquino", "Bautista",
    "Castillo", "Morales", "Perez", "Fernandez", "Rivera",
    "Navarro", "Soriano", "Pascual", "Aguilar", "Velasco",
    "Lim", "Tan", "Ong", "Sy", "Go",
    "Uy", "Chua", "Yu", "Co", "Kho",
    "Villanueva", "Domingo", "Salazar", "Mercado", "Tolentino",
    "Alvarez", "Manalo", "Panganiban", "Valdez", "David",
    "Abad", "Rosales", "Lao", "Macapagal", "Luna",
    "Bonifacio", "Rizal", "Mabini", "Ocampo", "Cortez",
]

course_codes = [c[0] for c in courses]
students = []
used_ids = set()

random.seed(42)  # fixed seed so data is consistent every run

for i in range(1500):
    year = random.randint(2021, 2025)
    while True:
        seq = random.randint(1, 9999)
        sid = f"{year}-{seq:04d}"
        if sid not in used_ids:
            used_ids.add(sid)
            break

    gender = random.choice(["Male", "Female"])
    first  = random.choice(first_names_male if gender == "Male" else first_names_female)
    last   = random.choice(last_names)
    year_level = random.randint(1, 4)
    coursecode = random.choice(course_codes)

    students.append((sid, first, last, year_level, gender, coursecode))

cursor.executemany(
    "INSERT IGNORE INTO Students "
    "(id, first_name, last_name, year_level, gender, coursecode, photo_url) "
    "VALUES (%s, %s, %s, %s, %s, %s, NULL)",
    students,
)

connection.commit()
connection.close()

print("Seed data inserted successfully.")
print(f"  {len(colleges)} colleges, {len(courses)} courses, {len(students)} students.")
