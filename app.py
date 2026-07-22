from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "student_tracker"


# -------------------------------
# Home Page
# -------------------------------
@app.route("/")
def home():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

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

        try:
            conn = sqlite3.connect("students.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO students (roll_no, name) VALUES (?, ?)",
                (roll, name)
            )

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "❌ Roll Number already exists!"

        finally:
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

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE roll_no = ?",
            (roll,)
        )

        student = cursor.fetchone()

        if student is None:
           conn.close()
           return "❌ Student not found! Please add the student first."

        cursor.execute(
            "INSERT INTO grades (roll_no, subject, marks) VALUES (?, ?, ?)",
            (roll, subject, marks)
        )

        conn.commit()
        conn.close()

        flash("✅ Grades added successfully!")
        return redirect(url_for("home"))
    return render_template("add_grades.html")

# -------------------------------
# View Students
# -------------------------------
@app.route("/students")
def students():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
            SELECT roll_no, name
            FROM students
            ORDER BY CAST(roll_no AS INTEGER) ASC
    """)

    students = cursor.fetchall()

    conn.close()

    return render_template("students.html", students=students)

# -------------------------------
# Average Report
# -------------------------------
@app.route("/average", methods=["GET", "POST"])
def average():

    avg = None
    message = None

    if request.method == "POST":

        class_name = request.form["class"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

         cursor.execute("""
            SELECT AVG(grades.marks)
            FROM students
            JOIN grades
            ON students.roll_no = grades.roll_no
            WHERE students.class = ?
        """, (class_name,))

        avg = cursor.fetchone()

        if avg is None:
            message = "❌ Class not found"

        conn.close()

    return render_template("average.html", avg=avg, message=message)

@app.route("/search_student", methods=["GET", "POST"])
def search_student():

    student = None
    searched = False

    if request.method == "POST":

        searched = True
        roll = request.form["roll"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT roll_no, name FROM students WHERE roll_no = ?",
            (roll,)
        )

        student = cursor.fetchone()

        conn.close()

    return render_template(
        "search_student.html",
        student=student,
        searched=searched
    )

@app.route("/topper", methods=["GET", "POST"])
def topper():

    topper = None
    message = None

    if request.method == "POST":

        subject = request.form["subject"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT students.roll_no,
                   students.name,
                   grades.subject,
                   grades.marks
            FROM students
            JOIN grades
            ON students.roll_no = grades.roll_no
            WHERE grades.subject = ?
            ORDER BY grades.marks DESC
            LIMIT 1
        """, (subject,))

        topper = cursor.fetchone()

        if topper is None:
            message = "❌ Subject not found"

        conn.close()

    return render_template("topper.html", topper=topper, message=message)

@app.route("/class_average", methods=["GET", "POST"])
def class_average():

    average = None
    subject = ""

    if request.method == "POST":

        subject = request.form["subject"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT AVG(marks) FROM grades WHERE subject = ?",
            (subject,)
        )

        result = cursor.fetchone()

        if result and result[0] is not None:
            average = round(result[0], 2)

        conn.close()

    return render_template(
        "class_average.html",
        average=average,
        subject=subject
    )

# -------------------------------
# Run Flask
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)