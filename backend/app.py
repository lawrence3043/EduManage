from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector


app = Flask(__name__)
CORS(app)


# ==================================================
#                 DATABASE CONNECTION
# ==================================================

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="edumanage",
        use_pure=True
    )


db = get_db_connection()


# ==================================================
#                    HOME ROUTE
# ==================================================

@app.route("/")
def home():

    return "EduManage Backend is Running and MySQL is Connected!"


# ==================================================
#                  STUDENT MANAGEMENT
# ==================================================


# =========================
# GET ALL STUDENTS
# =========================

@app.route("/students", methods=["GET"])
def get_students():

    global db

    if not db.is_connected():
        db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            student_id,
            first_name,
            last_name,
            email,
            phone,
            date_of_birth
        FROM students
    """)

    students = cursor.fetchall()

    cursor.close()

    return jsonify(students)


# =========================
# ADD A NEW STUDENT
# =========================

@app.route("/students", methods=["POST"])
def add_student():

    global db

    if not db.is_connected():
        db = get_db_connection()

    data = request.get_json()

    user_id = data["user_id"]
    department_id = data["department_id"]
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    phone = data["phone"]
    date_of_birth = data["date_of_birth"]

    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO students
        (
            user_id,
            department_id,
            first_name,
            last_name,
            email,
            phone,
            date_of_birth
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        department_id,
        first_name,
        last_name,
        email,
        phone,
        date_of_birth
    ))

    db.commit()

    cursor.close()

    return jsonify({
        "message": "Student added successfully!"
    }), 201


# =========================
# UPDATE A STUDENT
# =========================

@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):

    global db

    if not db.is_connected():
        db = get_db_connection()

    data = request.get_json()

    department_id = data["department_id"]
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    phone = data["phone"]
    date_of_birth = data["date_of_birth"]

    cursor = db.cursor()

    cursor.execute("""
        UPDATE students
        SET
            department_id = %s,
            first_name = %s,
            last_name = %s,
            email = %s,
            phone = %s,
            date_of_birth = %s
        WHERE student_id = %s
    """, (
        department_id,
        first_name,
        last_name,
        email,
        phone,
        date_of_birth,
        student_id
    ))

    db.commit()

    cursor.close()

    return jsonify({
        "message": "Student updated successfully!"
    })


# =========================
# DELETE A STUDENT
# =========================

@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):

    global db

    if not db.is_connected():
        db = get_db_connection()

    cursor = db.cursor()

    # Check if the student has course enrollments
    cursor.execute("""
        SELECT COUNT(*)
        FROM enrollments
        WHERE student_id = %s
    """, (student_id,))

    enrollment_count = cursor.fetchone()[0]

    # Don't delete students who have enrollments
    if enrollment_count > 0:

        cursor.close()

        return jsonify({
            "message": "Cannot delete this student because they have course enrollments."
        }), 409

    # Delete the student
    cursor.execute("""
        DELETE FROM students
        WHERE student_id = %s
    """, (student_id,))

    db.commit()

    if cursor.rowcount == 0:

        cursor.close()

        return jsonify({
            "message": "Student not found."
        }), 404

    cursor.close()

    return jsonify({
        "message": "Student deleted successfully!"
    })


# ==================================================
#                  COURSE MANAGEMENT
# ==================================================


# =========================
# GET ALL COURSES
# =========================

@app.route("/courses", methods=["GET"])
def get_courses():

    global db

    if not db.is_connected():
        db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            courses.course_id,
            courses.department_id,
            courses.teacher_id,
            courses.course_name,
            courses.credits,

            departments.department_name,

            teachers.first_name AS teacher_first_name,
            teachers.last_name AS teacher_last_name

        FROM courses

        JOIN departments
            ON courses.department_id = departments.department_id

        JOIN teachers
            ON courses.teacher_id = teachers.teacher_id
    """)

    courses = cursor.fetchall()

    cursor.close()

    return jsonify(courses)


# =========================
# ADD A NEW COURSE
# =========================

@app.route("/courses", methods=["POST"])
def add_course():

    global db

    if not db.is_connected():
        db = get_db_connection()

    data = request.get_json()

    department_id = data["department_id"]
    teacher_id = data["teacher_id"]
    course_name = data["course_name"]
    credits = data["credits"]

    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO courses
        (
            department_id,
            teacher_id,
            course_name,
            credits
        )
        VALUES (%s, %s, %s, %s)
    """, (
        department_id,
        teacher_id,
        course_name,
        credits
    ))

    db.commit()

    cursor.close()

    return jsonify({
        "message": "Course added successfully!"
    }), 201


# =========================
# UPDATE A COURSE
# =========================

@app.route("/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):

    global db

    if not db.is_connected():
        db = get_db_connection()

    data = request.get_json()

    department_id = data["department_id"]
    teacher_id = data["teacher_id"]
    course_name = data["course_name"]
    credits = data["credits"]

    cursor = db.cursor()

    cursor.execute("""
        UPDATE courses
        SET
            department_id = %s,
            teacher_id = %s,
            course_name = %s,
            credits = %s
        WHERE course_id = %s
    """, (
        department_id,
        teacher_id,
        course_name,
        credits,
        course_id
    ))

    db.commit()

    if cursor.rowcount == 0:

        cursor.close()

        return jsonify({
            "message": "Course not found."
        }), 404

    cursor.close()

    return jsonify({
        "message": "Course updated successfully!"
    })


# =========================
# DELETE A COURSE
# =========================

@app.route("/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):

    global db

    if not db.is_connected():
        db = get_db_connection()

    cursor = db.cursor()

    # Check if students are enrolled in this course
    cursor.execute("""
        SELECT COUNT(*)
        FROM enrollments
        WHERE course_id = %s
    """, (course_id,))

    enrollment_count = cursor.fetchone()[0]

    # Don't delete courses that have enrollments
    if enrollment_count > 0:

        cursor.close()

        return jsonify({
            "message": "Cannot delete this course because students are enrolled in it."
        }), 409

    # Delete the course
    cursor.execute("""
        DELETE FROM courses
        WHERE course_id = %s
    """, (course_id,))

    db.commit()

    if cursor.rowcount == 0:

        cursor.close()

        return jsonify({
            "message": "Course not found."
        }), 404

    cursor.close()

    return jsonify({
        "message": "Course deleted successfully!"
    })


# ==================================================
#                ENROLLMENT MANAGEMENT
# ==================================================


# =========================
# GET ALL ENROLLMENTS
# =========================

@app.route("/enrollments", methods=["GET"])
def get_enrollments():

    global db

    if not db.is_connected():
        db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            enrollments.enrollment_id,
            enrollments.student_id,
            enrollments.course_id,
            enrollments.enrollment_date,

            students.first_name AS student_first_name,
            students.last_name AS student_last_name,

            courses.course_name

        FROM enrollments

        JOIN students
            ON enrollments.student_id = students.student_id

        JOIN courses
            ON enrollments.course_id = courses.course_id

        ORDER BY enrollments.enrollment_id DESC
    """)

    enrollments = cursor.fetchall()

    cursor.close()

    return jsonify(enrollments)


# =========================
# ADD A NEW ENROLLMENT
# =========================

@app.route("/enrollments", methods=["POST"])
def add_enrollment():

    global db

    if not db.is_connected():
        db = get_db_connection()

    data = request.get_json()

    student_id = data["student_id"]
    course_id = data["course_id"]
    enrollment_date = data["enrollment_date"]

    cursor = db.cursor()

    # Check if the student is already enrolled
    cursor.execute("""
        SELECT COUNT(*)
        FROM enrollments
        WHERE student_id = %s
        AND course_id = %s
    """, (student_id, course_id))

    existing_enrollment = cursor.fetchone()[0]

    if existing_enrollment > 0:

        cursor.close()

        return jsonify({
            "message": "This student is already enrolled in this course."
        }), 409

    # Add the enrollment
    cursor.execute("""
        INSERT INTO enrollments
        (
            student_id,
            course_id,
            enrollment_date
        )
        VALUES (%s, %s, %s)
    """, (
        student_id,
        course_id,
        enrollment_date
    ))

    db.commit()

    cursor.close()

    return jsonify({
        "message": "Student enrolled successfully!"
    }), 201


# ==================================================
#                DEPARTMENT MANAGEMENT
# ==================================================


# =========================
# GET ALL DEPARTMENTS
# =========================

@app.route("/departments", methods=["GET"])
def get_departments():

    global db

    if not db.is_connected():
        db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            department_id,
            department_name
        FROM departments
    """)

    departments = cursor.fetchall()

    cursor.close()

    return jsonify(departments)


# ==================================================
#                  TEACHER MANAGEMENT
# ==================================================


# =========================
# GET ALL TEACHERS
# =========================

@app.route("/teachers", methods=["GET"])
def get_teachers():

    global db

    if not db.is_connected():
        db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            teacher_id,
            first_name,
            last_name
        FROM teachers
    """)

    teachers = cursor.fetchall()

    cursor.close()

    return jsonify(teachers)


# ==================================================
#                    RUN SERVER
# ==================================================

if __name__ == "__main__":

    app.run(debug=True)