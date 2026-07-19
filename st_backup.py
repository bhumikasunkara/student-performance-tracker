# ==========================================
# Student Performance Tracker
# Assignment A4
# Part 1
# ==========================================

import sqlite3


# ------------------------------------------
# Create Database
# ------------------------------------------
def create_database():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Student Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            roll_no TEXT PRIMARY KEY,
            name TEXT
        )
    """)

    # Grades Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT,
            subject TEXT,
            marks REAL,
            FOREIGN KEY(roll_no) REFERENCES students(roll_no)
        )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------
# Student Class
# ------------------------------------------
class Student:

    def __init__(self, name, roll_no):

        self.name = name
        self.roll_no = roll_no
        self.grades = {}

    # Add Grade
    def add_grade(self, subject, marks):

        self.grades[subject] = marks

    # Calculate Average
    def calculate_average(self):

        if len(self.grades) == 0:
            return 0

        return sum(self.grades.values()) / len(self.grades)

    # Display Student Details
    def display(self):

        print("\n" + "=" * 40)
        print("         STUDENT DETAILS")
        print("=" * 40)
        print(f"Name     : {self.name}")
        print(f"Roll No  : {self.roll_no}")

        if len(self.grades) == 0:

            print("\nNo grades available.")

        else:

            print("\nGrades:")

            for subject, marks in self.grades.items():
                print(f"{subject} : {marks}")

            print(f"\nAverage : {self.calculate_average():.2f}")

# ------------------------------------------
# Student Tracker Class
# ------------------------------------------

class StudentTracker:

    def __init__(self):

        self.students = []

    # --------------------------------------
    # Find Student
    # --------------------------------------
    def find_student(self, roll):

        for student in self.students:

            if student.roll_no == roll:
                return student

        return None

    # --------------------------------------
    # Add Student
    # --------------------------------------
    def add_student(self):

        print("\n========== ADD STUDENT ==========")

        name = input("Enter Student Name : ")
        roll = input("Enter Roll Number  : ")

        # Check duplicate roll number
        if self.find_student(roll):

            print("\nRoll Number already exists!")
            return

        student = Student(name, roll)

        self.students.append(student)

        # Save to Database
        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO students (roll_no, name) VALUES (?, ?)",
            (roll, name)
        )

        conn.commit()
        conn.close()

        print("\nStudent Added Successfully!")

    # --------------------------------------
    # Load Students from Database
    # --------------------------------------
    def load_students(self):

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("SELECT roll_no, name FROM students")

        records = cursor.fetchall()

        conn.close()

        for roll, name in records:

            student = Student(name, roll)

            db = sqlite3.connect("students.db")
            cur = db.cursor()

            cur.execute(
                "SELECT subject, marks FROM grades WHERE roll_no=?",
                (roll,)
            )

            grades = cur.fetchall()

            db.close()

            for subject, marks in grades:

                student.add_grade(subject, marks)

            self.students.append(student)

# ------------------------------------------
# Display Menu
# ------------------------------------------

def menu():

    print("\n")
    print("=" * 45)
    print("     STUDENT PERFORMANCE TRACKER")
    print("=" * 45)
    print("1. Add Student")
    print("2. Add Grades")
    print("3. View Student")
    print("4. Calculate Average")
    print("5. Exit")
    print("=" * 45)


# ------------------------------------------
# Add Grades
# ------------------------------------------

def add_grades(tracker):

    print("\n========== ADD GRADES ==========")

    roll = input("Enter Roll Number : ")

    student = tracker.find_student(roll)

    if student is None:

        print("\nStudent not found!")
        return

    while True:

        subject = input("\nEnter Subject Name (or 'done' to finish): ").title()

        if subject.lower() == "done":
            break

        try:

            marks = float(input(f"Enter Marks for {subject} : "))

            if marks < 0 or marks > 100:

                print("Marks should be between 0 and 100.")
                continue

            # Save in object
            student.add_grade(subject, marks)

            # Save in database
            conn = sqlite3.connect("students.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO grades (roll_no, subject, marks) VALUES (?, ?, ?)",
                (roll, subject, marks)
            )

            conn.commit()
            conn.close()

            print("Grade Added Successfully!")

        except ValueError:

            print("Please enter valid marks.")


# ------------------------------------------
# View Student
# ------------------------------------------

def view_student(tracker):

    print("\n========== VIEW STUDENT ==========")

    roll = input("Enter Roll Number : ")

    student = tracker.find_student(roll)

    if student is None:

        print("\nStudent not found!")

    else:

        student.display()


# ------------------------------------------
# Calculate Average
# ------------------------------------------

def calculate_average(tracker):

    print("\n====== CALCULATE AVERAGE ======")

    roll = input("Enter Roll Number : ")

    student = tracker.find_student(roll)

    if student is None:

        print("\nStudent not found!")

    else:

        print(f"\nAverage Marks : {student.calculate_average():.2f}")

# ------------------------------------------
# Main Function
# ------------------------------------------

def main():

    # Create database if it doesn't exist
    create_database()

    tracker = StudentTracker()

    # Load existing students from database
    tracker.load_students()

    print("\nWelcome to Student Performance Tracker!")

    while True:

        menu()

        choice = input("Enter your choice : ")

        if choice == "1":

            tracker.add_student()

        elif choice == "2":

            add_grades(tracker)

        elif choice == "3":

            view_student(tracker)

        elif choice == "4":

            calculate_average(tracker)

        elif choice == "5":

            print("\nThank you for using Student Performance Tracker!")
            break

        else:

            print("\nInvalid Choice! Please try again.")


# ------------------------------------------
# Run Program
# ------------------------------------------

if __name__ == "__main__":

    main()