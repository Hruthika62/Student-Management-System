
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "student-management-secret"

DATABASE = "students.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            usn TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    search = request.args.get("search", "").strip()

    conn = get_db()

    if search:
        students = conn.execute("""
            SELECT * FROM students
            WHERE name LIKE ? OR usn LIKE ? OR course LIKE ?
            ORDER BY id DESC
        """, (f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()
    else:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        students=students,
        search=search
    )


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"].strip()
    usn = request.form["usn"].strip()
    email = request.form["email"].strip()
    course = request.form["course"].strip()

    if not all([name, usn, email, course]):
        flash("Please fill in all fields.", "error")
        return redirect(url_for("index"))

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO students (name, usn, email, course)
            VALUES (?, ?, ?, ?)
        """, (name, usn, email, course))

        conn.commit()
        flash("Student added successfully!", "success")

    except sqlite3.IntegrityError:
        flash("This USN already exists.", "error")

    finally:
        conn.close()

    return redirect(url_for("index"))


@app.route("/edit/<int:student_id>", methods=["POST"])
def edit_student(student_id):
    name = request.form["name"].strip()
    usn = request.form["usn"].strip()
    email = request.form["email"].strip()
    course = request.form["course"].strip()

    conn = get_db()

    try:
        conn.execute("""
            UPDATE students
            SET name = ?, usn = ?, email = ?, course = ?
            WHERE id = ?
        """, (name, usn, email, course, student_id))

        conn.commit()
        flash("Student updated successfully!", "success")

    except sqlite3.IntegrityError:
        flash("This USN already belongs to another student.", "error")

    finally:
        conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    flash("Student deleted successfully!", "success")

    return redirect(url_for("index"))


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=False)
