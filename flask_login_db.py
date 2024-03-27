from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

app = Flask(__name__, template_folder='template')
app.secret_key = 'secret_key'  # Set a secret key for the session

# Verbindung zur SQLite-Datenbank herstellen
conn = sqlite3.connect('Login_DB.db', check_same_thread=False)
cursor = conn.cursor()

# Tabelle erstellen, falls sie noch nicht existiert
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Daten aus der Datenbank abrufen
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            stored_password = user[2]  # Index 2 entspricht dem verschlüsselten Passwort in der Datenbank
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                session['username'] = username  # Create a session upon successful login
                return redirect(url_for('dashboard'))
            else:
                return render_template('index_login_db.html', error='Invalid password')
        else:
            return render_template('register.html', error='User does not exist')

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear the session upon logout
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            # Überprüfen, ob der Benutzer bereits existiert
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                stored_password = existing_user[2]
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    session['username'] = username  # Log in the user immediately
                    return redirect(url_for('dashboard'))
                else:
                    return render_template('register.html', error='Invalid password. Please log in.')

            # Passwort hashen und in die Datenbank einfügen
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()

            session['username'] = username  # Create a session upon successful registration
            return render_template('index_login_db.html', message='User created. Please log in.')

        except Exception as e:
            print(f"Error during registration: {e}")
            return render_template('register.html', error='An error occurred during registration')

    return render_template('register.html')


app.run()
