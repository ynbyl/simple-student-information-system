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
    ("CCS",  "College of Computer Studies"),
    ("CED",  "College of Education"),
    ("CBA",  "College of Business Administration"),
    ("COE",  "College of Engineering"),
    ("CON",  "College of Nursing"),
    ("CAS",  "College of Arts and Sciences"),
    ("CAF",  "College of Agriculture and Forestry"),
    ("CCJ",  "College of Criminal Justice"),
    ("CAR",  "College of Architecture"),
    ("CPH",  "College of Public Health"),
]
cursor.executemany(
    "INSERT IGNORE INTO Colleges (collegecode, collegename) VALUES (%s, %s)",
    colleges,
)

# ── 30 Courses (3 per college) ────────────────────────────────────────────────
courses = [
    # CCS
    ("BSCS",  "Bachelor of Science in Computer Science",              "CCS"),
    ("BSIT",  "Bachelor of Science in Information Technology",        "CCS"),
    ("BSIS",  "Bachelor of Science in Information Systems",           "CCS"),
    # CED
    ("BSED",  "Bachelor of Secondary Education",                      "CED"),
    ("BEED",  "Bachelor of Elementary Education",                     "CED"),
    ("BSPE",  "Bachelor of Physical Education",                       "CED"),
    # CBA
    ("BSBA",  "Bachelor of Science in Business Administration",       "CBA"),
    ("BSA",   "Bachelor of Science in Accountancy",                   "CBA"),
    ("BSEM",  "Bachelor of Science in Entrepreneurship Management",   "CBA"),
    # COE
    ("BSCE",  "Bachelor of Science in Civil Engineering",             "COE"),
    ("BSEE",  "Bachelor of Science in Electrical Engineering",        "COE"),
    ("BSME",  "Bachelor of Science in Mechanical Engineering",        "COE"),
    # CON
    ("BSN",   "Bachelor of Science in Nursing",                       "CON"),
    ("BSMID", "Bachelor of Science in Midwifery",                     "CON"),
    ("BSMT",  "Bachelor of Science in Medical Technology",            "CON"),
    # CAS
    ("BSPS",  "Bachelor of Science in Psychology",                    "CAS"),
    ("ABSOC", "Bachelor of Arts in Sociology",                        "CAS"),
    ("ABCOM", "Bachelor of Arts in Communication",                    "CAS"),
    # CAF
    ("BSAG",  "Bachelor of Science in Agriculture",                   "CAF"),
    ("BSFOR", "Bachelor of Science in Forestry",                      "CAF"),
    ("BSFT",  "Bachelor of Science in Food Technology",               "CAF"),
    # CCJ
    ("BSCRIM","Bachelor of Science in Criminology",                   "CCJ"),
    ("BSFS",  "Bachelor of Science in Forensic Science",              "CCJ"),
    ("BSLS",  "Bachelor of Science in Legal Studies",                 "CCJ"),
    # CAR
    ("BSAR",  "Bachelor of Science in Architecture",                  "CAR"),
    ("BSID",  "Bachelor of Science in Interior Design",               "CAR"),
    ("BSFAD", "Bachelor of Fine Arts and Design",                     "CAR"),
    # CPH
    ("BSPH",  "Bachelor of Science in Public Health",                 "CPH"),
    ("BSND",  "Bachelor of Science in Nutrition and Dietetics",       "CPH"),
    ("BSRM",  "Bachelor of Science in Radiologic Technology",         "CPH"),
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
