from flask import Flask, render_template, request, redirect, send_from_directory
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

teacher_username = "admin"
teacher_password = "1234"

videos = []
doubts = {}


# ================= DATABASE =================

def init_db():

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        sid TEXT,
        roll TEXT
    )
    ''')

    conn.commit()
    conn.close()


init_db()


# ================= HOME =================

@app.route('/')
def home():

    return render_template('index.html')


# ================= TEACHER LOGIN =================

@app.route('/teacher', methods=['GET', 'POST'])
def teacher():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == teacher_username and password == teacher_password:

            conn = sqlite3.connect('students.db')

            cursor = conn.cursor()

            cursor.execute("SELECT * FROM students")

            students = cursor.fetchall()

            conn.close()

            notes = os.listdir('uploads')

            return render_template(
                'teacher.html',
                students=students,
                notes=notes,
                videos=videos,
                doubts=doubts
            )

    return render_template('teacher_login.html')


# ================= STUDENT LOGIN =================

@app.route('/student', methods=['GET', 'POST'])
def student_login():

    if request.method == 'POST':

        sid = request.form['student_id']
        roll = request.form['roll']

        conn = sqlite3.connect('students.db')

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE sid=? AND roll=?",
            (sid, roll)
        )

        student = cursor.fetchone()

        conn.close()

        if student:

            student_data = {
                'id': student[0],
                'name': student[1],
                'sid': student[2],
                'roll': student[3]
            }

            notes = os.listdir('uploads')

            return render_template(
                'student.html',
                student=student_data,
                notes=notes,
                videos=videos,
                doubts=doubts
            )

    return render_template('student_login.html')


# ================= ADD STUDENT =================

@app.route('/add_student', methods=['POST'])
def add_student():

    name = request.form['name']
    sid = request.form['sid']
    roll = request.form['roll']

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students(name, sid, roll) VALUES (?, ?, ?)",
        (name, sid, roll)
    )

    conn.commit()
    conn.close()

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    notes = os.listdir('uploads')

    return render_template(
        'teacher.html',
        students=students,
        notes=notes,
        videos=videos,
        doubts=doubts
    )


# ================= DELETE STUDENT =================

@app.route('/delete_student/<int:id>')
def delete_student(id):

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    notes = os.listdir('uploads')

    return render_template(
        'teacher.html',
        students=students,
        notes=notes,
        videos=videos,
        doubts=doubts
    )


# ================= UPLOAD NOTES =================

@app.route('/upload_note', methods=['POST'])
def upload_note():

    file = request.files['note']

    if file:

        file.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                file.filename
            )
        )

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    notes = os.listdir('uploads')

    return render_template(
        'teacher.html',
        students=students,
        notes=notes,
        videos=videos,
        doubts=doubts
    )


# ================= DELETE NOTES =================

@app.route('/delete_note/<filename>')
def delete_note(filename):

    path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        filename
    )

    if os.path.exists(path):

        os.remove(path)

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    notes = os.listdir('uploads')

    return render_template(
        'teacher.html',
        students=students,
        notes=notes,
        videos=videos,
        doubts=doubts
    )


# ================= DOWNLOAD NOTES =================

@app.route('/uploads/<filename>')
def uploaded_file(filename):

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )


# ================= ADD VIDEO =================

@app.route('/add_video', methods=['POST'])
def add_video():

    title = request.form['title']
    link = request.form['link']

    videos.append({
        'title': title,
        'link': link
    })

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    notes = os.listdir('uploads')

    return render_template(
        'teacher.html',
        students=students,
        notes=notes,
        videos=videos,
        doubts=doubts
    )


# ================= DELETE VIDEO =================

@app.route('/delete_video/<int:index>')
def delete_video(index):

    if index < len(videos):

        videos.pop(index)

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    notes = os.listdir('uploads')

    return render_template(
        'teacher.html',
        students=students,
        notes=notes,
        videos=videos,
        doubts=doubts
    )


# ================= SEND DOUBT =================

@app.route('/send_doubt', methods=['POST'])
def send_doubt():

    student_name = request.form['student_name']
    message = request.form['message']

    if student_name not in doubts:

        doubts[student_name] = []

    doubts[student_name].append({
        'question': message,
        'reply': ''
    })

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE name=?",
        (student_name,)
    )

    student = cursor.fetchone()

    conn.close()

    student_data = {
        'id': student[0],
        'name': student[1],
        'sid': student[2],
        'roll': student[3]
    }

    notes = os.listdir('uploads')

    return render_template(
        'student.html',
        student=student_data,
        notes=notes,
        videos=videos,
        doubts=doubts
    )


# ================= REPLY DOUBT =================

@app.route('/reply_doubt/<student>/<int:index>', methods=['POST'])
def reply_doubt(student, index):

    reply = request.form['reply']

    doubts[student][index]['reply'] = reply

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    notes = os.listdir('uploads')

    return render_template(
        'teacher.html',
        students=students,
        notes=notes,
        videos=videos,
        doubts=doubts
    )


# ================= DELETE DOUBT =================

@app.route('/delete_doubt/<student>/<int:index>')
def delete_doubt(student, index):

    if student in doubts:

        if index < len(doubts[student]):

            doubts[student].pop(index)

    conn = sqlite3.connect('students.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    notes = os.listdir('uploads')

    return render_template(
        'teacher.html',
        students=students,
        notes=notes,
        videos=videos,
        doubts=doubts
    )


# ================= RUN APP =================

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)