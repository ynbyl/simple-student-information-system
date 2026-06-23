# this script creates the database and tables
# run this first before running the app
# python database.py

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

# ── 10 Colleges ──────────────────────────────────────────────────────────────
colleges = [
    ("CASS", "College of Arts and Social Sciences"),
    ("CCS",  "College of Computer Studies"),
    ("CSM",  "College of Science and Mathematics"),
    ("CED",  "College of Education"),
    ("CEBA", "College of Economics, Business and Accountancy"),
]
cursor.executemany(
    "INSERT IGNORE INTO Colleges (collegecode, collegename) VALUES (%s, %s)",
    colleges,
)

# ── 30 Courses (3 per college) ────────────────────────────────────────────────
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

    ("BSME",   "Bachelor of Science in Mathematics Education",      "CED"),
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
]
cursor.executemany(
    "INSERT IGNORE INTO Courses (coursecode, coursename, collegecode) VALUES (%s, %s, %s)",
    courses,
)

# ── 300 Students ─────────────────────────────────────────────────────────────
first_names_male = [
    "Juan", "Pedro", "Carlos", "Miguel", "Andres", "Ramon", "Jose", "Luis",
    "Mario", "Eduardo", "Roberto", "Antonio", "Francisco", "Manuel", "Diego",
    "Gabriel", "Rafael", "Daniel", "Marco", "Paolo", "Liam", "Ethan", "Nathan",
    "Kevin", "Aaron", "Bryan", "Christian", "Jerome", "Kenneth", "Leonard",
]
first_names_female = [
    "Maria", "Ana", "Lucia", "Sofia", "Isabella", "Gabriela", "Rosa", "Elena",
    "Carmen", "Teresa", "Patricia", "Monica", "Sandra", "Angela", "Cristina",
    "Diana", "Laura", "Claudia", "Vanessa", "Maricel", "Hannah", "Nicole",
    "Jasmine", "Camille", "Tricia", "Abigail", "Rachelle", "Joanna", "Melissa",
    "Stephanie",
]
last_names = [
    "Dela Cruz", "Santos", "Reyes", "Garcia", "Lopez", "Mendoza", "Torres",
    "Ramos", "Flores", "Cruz", "Aquino", "Villanueva", "Bautista", "Castillo",
    "Morales", "Gonzalez", "Hernandez", "Perez", "Ramirez", "Fernandez",
    "Rivera", "Navarro", "Soriano", "Pascual", "Aguilar", "Velasco", "Espinosa",
    "Lim", "Tan", "Ong", "Sy", "Go", "Chan", "Domingo", "Macapagal",
    "Bonifacio", "Rizal", "Mabini", "Luna", "Ocampo",
]

course_codes = [c[0] for c in courses]

students = []
used_ids = set()

random.seed(42)  # fixed seed so the data is consistent every run

for i in range(300):
    # generate a unique YYYY-NNNN id
    year = random.randint(2019, 2024)
    while True:
        seq = random.randint(1, 9999)
        sid = f"{year}-{seq:04d}"
        if sid not in used_ids:
            used_ids.add(sid)
            break

    gender = random.choice(["Male", "Female"])
    if gender == "Male":
        first = random.choice(first_names_male)
    else:
        first = random.choice(first_names_female)

    last = random.choice(last_names)
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
