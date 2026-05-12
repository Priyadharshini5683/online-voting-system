from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            voted INTEGER DEFAULT 0
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS votes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------

@app.route('/')
def home():
    return render_template('index.html')

# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )
            conn.commit()
            return redirect('/login')

        except:
            return "User already exists"

        finally:
            conn.close()

    return render_template('register.html')

# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect('/vote')

        else:
            return "Invalid Login"

    return render_template('login.html')

# ---------------- VOTING ----------------

@app.route('/vote', methods=['GET', 'POST'])
def vote():

    if 'username' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute(
        "SELECT voted FROM users WHERE username=?",
        (session['username'],)
    )

    voted = cur.fetchone()[0]

    if voted == 1:
        return "You already voted"

    if request.method == 'POST':

        candidate = request.form['candidate']

        cur.execute(
            "INSERT INTO votes(candidate) VALUES(?)",
            (candidate,)
        )

        cur.execute(
            "UPDATE users SET voted=1 WHERE username=?",
            (session['username'],)
        )

        conn.commit()
        conn.close()

        return redirect('/result')

    return render_template('vote.html')

# ---------------- RESULT ----------------

@app.route('/result')
def result():

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT candidate, COUNT(candidate)
        FROM votes
        GROUP BY candidate
    """)

    results = cur.fetchall()

    conn.close()

    return render_template('result.html', results=results)

# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(debug=True)
