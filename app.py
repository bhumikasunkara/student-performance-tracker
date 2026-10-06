from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "student_tracker"


# -------------------------------
# Database Connection
# -------------------------------
def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL is not configured")

    conn = psycopg2.connect(database_url)
    return conn


# -------------------------------
# Initialize Database
# -------------------------------
def init_db():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            roll_no VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id SERIAL PRIMARY KEY,
            roll_no VARCHAR(50) NOT NULL,
            subject VARCHAR(100) NOT NULL,
            marks NUMERIC NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# -------------------------------
# Home Page
# -------------------------------
@app.route("/")
def home():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        total_students=total_students
    )


# -------------------------------
# Add Student
# -------------------------------
@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]

        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO students (roll_no, name) VALUES (%s, %s)",
                (roll, name)
            )

            conn.commit()

        except psycopg2.IntegrityError:
            if conn:
                conn.rollback()

            return "❌ Roll Number already exists!"

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        flash("✅ Student added successfully!")
        return redirect(url_for("home"))

    return render_template("add_student.html")


# -------------------------------
# Add Grades
# -------------------------------
@app.route("/add_grades", methods=["GET", "POST"])
def add_grades():

    if request.method == "POST":

        roll = request.form["roll"]
        subject = request.form["subject"]
        marks = request.form["marks"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE roll_no = %s",
            (roll,)
        )

        student = cursor.fetchone()

        if student is None:
            cursor.close()
            conn.close()
            return "❌ Student not found! Please add the student first."

        cursor.execute(
            """
            INSERT INTO grades (roll_no, subject, marks)
            VALUES (%s, %s, %s)
            """,
            (roll, subject, marks)
        )

        conn.commit()

        cursor.close()
        conn.close()

        flash("✅ Grades added successfully!")
        return redirect(url_for("home"))

    return render_template("add_grades.html")


# -------------------------------
# View Students
# -------------------------------
@app.route("/students")
def students():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT roll_no, name
        FROM students
        ORDER BY CAST(roll_no AS INTEGER) ASC
    """)

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "students.html",
        students=students
    )


# -------------------------------
# Average Report
# -------------------------------
@app.route("/average", methods=["GET", "POST"])
def average():

    avg = None
    message = None
    subject = None

    if request.method == "POST":

        subject = request.form.get("subject")

        if not subject:
            message = "Please enter subject"

            return render_template(
                "average.html",
                avg=avg,
                subject=subject,
                message=message
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT AVG(marks)
            FROM grades
            WHERE subject = %s
        """, (subject,))

        avg = cursor.fetchone()

        if avg[0] is None:
            message = "❌ Subject not found"
        else:
            avg = round(float(avg[0]), 2)

        cursor.close()
        conn.close()

    return render_template(
        "average.html",
        avg=avg,
        subject=subject,
        message=message
    )


# -------------------------------
# Search Student
# -------------------------------
@app.route("/search_student", methods=["GET", "POST"])
def search_student():

    student = None
    searched = False

    if request.method == "POST":

        searched = True
        roll = request.form["roll"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT roll_no, name
            FROM students
            WHERE roll_no = %s
            """,
            (roll,)
        )

        student = cursor.fetchone()

        cursor.close()
        conn.close()

    return render_template(
        "search_student.html",
        student=student,
        searched=searched
    )


# -------------------------------
# Subject Topper
# -------------------------------
@app.route("/topper", methods=["GET", "POST"])
def topper():

    topper = None
    message = None

    if request.method == "POST":

        subject = request.form["subject"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT students.roll_no,
                   students.name,
                   grades.subject,
                   grades.marks
            FROM students
            JOIN grades
            ON students.roll_no = grades.roll_no
            WHERE grades.subject = %s
            ORDER BY grades.marks DESC
            LIMIT 1
        """, (subject,))

        topper = cursor.fetchone()

        if topper is None:
            message = "❌ Subject not found"

        cursor.close()
        conn.close()

    return render_template(
        "topper.html",
        topper=topper,
        message=message
    )


# -------------------------------
# Initialize Database
# -------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    init_db()