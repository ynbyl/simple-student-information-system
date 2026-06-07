# this script creates the database and tables
# run this first before running the app
# python database.py

import os

import mysql.connector
from dotenv import load_dotenv

# load the .env file so we can get the db credentials
load_dotenv()

# connect to mysql without selecting a database yet
db_config = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

DATABASE_NAME = os.getenv("DB_NAME", "ssis")

# create the database if it doesnt exist yet
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
cursor.execute(f"USE {DATABASE_NAME}")

# drop tables first so we can recreate them fresh
# need to drop in this order because of foreign keys
cursor.execute("DROP TABLE IF EXISTS Students")
cursor.execute("DROP TABLE IF EXISTS Courses")
cursor.execute("DROP TABLE IF EXISTS Colleges")

# create colleges table first since courses depend on it
cursor.execute(
    """
    CREATE TABLE Colleges (
        collegecode VARCHAR(255) PRIMARY KEY,
        collegename VARCHAR(255) NOT NULL
    )
    """
)

# courses belong to a college
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

# students belong to a course
cursor.execute(
    """
    CREATE TABLE Students (
        id          VARCHAR(255) PRIMARY KEY,
        first_name  VARCHAR(255) NOT NULL,
        last_name   VARCHAR(255) NOT NULL,
        year_level  INT          NOT NULL,
        gender      VARCHAR(255) NOT NULL,
        coursecode  VARCHAR(255),
        FOREIGN KEY (coursecode) REFERENCES Courses(coursecode)
    )
    """
)

connection.commit()
connection.close()

print(f"Database '{DATABASE_NAME}' and tables created successfully.")
