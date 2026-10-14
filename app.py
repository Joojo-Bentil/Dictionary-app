from flask import Flask, render_template, url_for, request, current_app, jsonify, redirect, session
from flaskext.mysql import MySQL 
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql.cursors
import csv
import uuid
import json
import datetime
import os

app = Flask(__name__)

app.secret_key = 'secret'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'dictionary'
mysql = MySQL(app, cursorclass=pymysql.cursors.DictCursor)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_response = ''
    if request.method == 'POST':
        user_input = request.form['word']
        if user_input == '':
            user_response = "You did not enter a valid word. Please try again."
        else:
            conn =mysql.get_db()
            cur = conn.cursor()
            cur.execute('SELECT meaning FROM word WHERE word = %s', (user_input))
            rv = cur.fetchall()
            if (len(rv) > 0):
                user_response = rv[0]['meaning']
            else:
                user_response = "Word not found in the dictionary."
        
        
    return render_template('index.html', user_response=user_response)

@app.route('/dashboard')
def dashboard():
    conn =mysql.get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM word')
    rv = cur.fetchall()
    
    return render_template('dashboard.html', words=rv)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('login.html')

    if request.is_json:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(success=False, message='Invalid sign-in data.'), 400
    else:
        data = request.form

    email = (data.get('email') or data.get('username') or '').strip()
    password = data.get('password') or ''
    if not email or not password:
        return jsonify(success=False, message='Wrong credentials.'), 401

    cur = None
    try:
        conn = mysql.get_db()
        cur = conn.cursor()
        cur.execute(
            'SELECT `id`, `password` FROM `user_registration` WHERE `email` = %s',
            (email,)
        )
        user = cur.fetchone()
    except pymysql.MySQLError:
        current_app.logger.exception('Failed to look up a user during sign in')
        return jsonify(
            success=False,
            message='Could not sign in right now. Please try again.'
        ), 500
    finally:
        if cur is not None:
            cur.close()

    if user is None or not check_password_hash(user['password'], password):
        return jsonify(success=False, message='Wrong credentials.'), 401

    session.clear()
    session['user_id'] = user['id']
    return jsonify(success=True, redirect=url_for('index'))


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'GET':
        return render_template('user_registration.html')

    if request.is_json:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(success=False, message='Invalid registration data.'), 400
    else:
        data = request.form

    fullname = (data.get('fullname') or data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    confirm_password = data.get('confirm_password') or ''

    if not fullname or not email or not password:
        message = 'Please complete all required fields.'
    elif len(fullname) > 100 or len(email) > 100:
        message = 'Full name and email must be 100 characters or fewer.'
    elif password != confirm_password:
        message = 'Passwords do not match.'
    else:
        message = None

    if message:
        if request.is_json:
            return jsonify(success=False, message=message), 400
        return render_template('user_registration.html', registration_error=message), 400

    password_hash = generate_password_hash(password)
    conn = None
    cur = None
    
    try:
        conn = mysql.get_db()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO `user_registration` (`fullname`, `email`, `password`) VALUES (%s, %s, %s)',
            (fullname, email, password_hash)
        )
        conn.commit()
    except pymysql.MySQLError:
        if conn is not None:
            conn.rollback()
        current_app.logger.exception('Failed to insert a user registration')
        if request.is_json:
            return jsonify(
                success=False,
                message='Could not save the registration. Check the Flask server log for the database error.'
            ), 500
        return render_template(
            'user_registration.html',
            registration_error='Could not save the registration. Please try again or contact the site administrator.'
        ), 500
    finally:
        if cur is not None:
            cur.close()

    if request.is_json:
        return jsonify(success=True, redirect=url_for('login')), 201
    return redirect(url_for('login'))


@app.route('/word', methods=['POST'])
def add_word():
    req = request.get_json()
    word = req['word']
    meaning = req['meaning']
    
    conn =mysql.get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO word (word, meaning) VALUES (%s, %s)', (word, meaning))
    conn.commit()
    cur.close()

    return json.dumps('success')


@app.route('/words/import', methods=['POST'])
def import_words():
    uploaded_file = request.files.get('csv_file')
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify(success=False, message='Select a CSV file to import.'), 400
    if not uploaded_file.filename.lower().endswith('.csv'):
        return jsonify(success=False, message='Only CSV files can be imported.'), 400

    upload_folder = os.path.join(current_app.root_path, 'static', 'files')
    os.makedirs(upload_folder, exist_ok=True)
    saved_path = os.path.join(upload_folder, f'{uuid.uuid4().hex}.csv')
    uploaded_file.save(saved_path)

    conn = None
    cur = None
    imported_count = 0
    batch = []
    try:
        conn = mysql.get_db()
        cur = conn.cursor()
        conn.begin()

        with open(saved_path, newline='', encoding='utf-8-sig') as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)
            for row_number, row in enumerate(reader, start=2):
                if not row or all(not value.strip() for value in row):
                    continue
                if len(row) < 2 or not row[0].strip() or not row[1].strip():
                    raise ValueError(
                        f'CSV row {row_number} must contain both a word and a meaning.'
                    )
                batch.append((row[0].strip(), row[1].strip()))
                if len(batch) >= 1000:
                    cur.executemany(
                        'INSERT INTO `word` (`word`, `meaning`) VALUES (%s, %s)',
                        batch
                    )
                    imported_count += len(batch)
                    batch.clear()

        if batch:
            cur.executemany(
                'INSERT INTO `word` (`word`, `meaning`) VALUES (%s, %s)',
                batch
            )
            imported_count += len(batch)

        if imported_count == 0:
            conn.rollback()
            return jsonify(success=False, message='The CSV contains no word rows to import.'), 400
        conn.commit()
    except (UnicodeDecodeError, csv.Error, ValueError) as error:
        if conn is not None:
            conn.rollback()
        return jsonify(success=False, message=str(error)), 400
    except pymysql.MySQLError:
        if conn is not None:
            conn.rollback()
        current_app.logger.exception('Failed to import words from CSV')
        return jsonify(
            success=False,
            message='The CSV could not be imported because of a database error.'
        ), 500
    finally:
        if cur is not None:
            cur.close()

    return jsonify(
        success=True,
        message=f'Successfully imported {imported_count} words.',
        imported_count=imported_count
    )


@app.route('/word/<id>/delete', methods=['POST'])
def delete_word(id):
    word_id = id
    conn =mysql.get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM word WHERE id = %s', (word_id,))
    conn.commit()
    cur.close()

    return json.dumps('success')

@app.route('/word/<id>/edit', methods=['POST'])
def edit_word(id):
    word_id = id
    req = request.get_json()
    word = req['word']
    meaning = req['meaning']
    
    conn =mysql.get_db()
    cur = conn.cursor()
    cur.execute('UPDATE word SET word = %s, meaning = %s WHERE id = %s', (word, meaning, word_id))
    conn.commit()
    cur.close()

    return json.dumps('success')

@app.route('/add_logo', methods=['POST'])
def add_logo():
    image = request.files['file']
    
    if image:
        filepath = os.path.join(current_app.root_path, 'static/images/logo.png')
        image.save(filepath)
    return 'success'

if __name__ == "__main__":
    app.run(debug=True)