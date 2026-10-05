from flask import Flask, render_template, url_for, request, current_app
from flaskext.mysql import MySQL 
import pymysql.cursors
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add your login logic here
    return render_template('login.html')
    

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