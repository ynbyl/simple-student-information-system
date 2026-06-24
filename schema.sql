-- database schema for the SSIS project
-- run this to set up the database
-- mysql -u root -p < schema.sql

-- create the database if it doesnt exist yet
CREATE DATABASE IF NOT EXISTS ssis
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ssis;

-- drop tables first before recreating them
-- need to drop in this order because of the foreign keys
DROP TABLE IF EXISTS Students;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Colleges;

-- colleges table (parent table, everything depends on this)
CREATE TABLE Colleges (
    collegecode VARCHAR(20)  NOT NULL,
    collegename VARCHAR(255) NOT NULL,

    CONSTRAINT pk_colleges PRIMARY KEY (collegecode)
) ENGINE=InnoDB
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- courses table, each course belongs to a college
CREATE TABLE Courses (
    coursecode  VARCHAR(20)  NOT NULL,
    coursename  VARCHAR(255) NOT NULL,
    collegecode VARCHAR(20)  NULL,

    CONSTRAINT pk_courses PRIMARY KEY (coursecode),
    CONSTRAINT fk_course_college
        FOREIGN KEY (collegecode)
        REFERENCES Colleges (collegecode)
        ON UPDATE CASCADE
        ON DELETE CASCADE  -- if college is deleted, courses get deleted too
) ENGINE=InnoDB
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- students table, each student is enrolled in a course
CREATE TABLE Students (
    id          VARCHAR(20)  NOT NULL,
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100) NOT NULL,
    year_level  TINYINT      NOT NULL CHECK (year_level BETWEEN 1 AND 4),
    gender      ENUM('Male', 'Female') NOT NULL,
    coursecode  VARCHAR(20)  NULL,
    photo_url   VARCHAR(500) NULL,  -- profile photo from cloudinary, optional

    CONSTRAINT pk_students PRIMARY KEY (id),
    CONSTRAINT fk_student_course
        FOREIGN KEY (coursecode)
        REFERENCES Courses (coursecode)
        ON UPDATE CASCADE
        ON DELETE CASCADE  -- if course is deleted, students get deleted too
) ENGINE=InnoDB
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- indexes to make search faster
CREATE INDEX idx_colleges_name   ON Colleges (collegename);
CREATE INDEX idx_courses_name    ON Courses  (coursename);
CREATE INDEX idx_courses_college ON Courses  (collegecode);
CREATE INDEX idx_students_last   ON Students (last_name);
CREATE INDEX idx_students_first  ON Students (first_name);
CREATE INDEX idx_students_course ON Students (coursecode);