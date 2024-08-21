from flask import Flask, render_template, request, send_from_directory ,redirect
import sqlite3
import os
import uuid
import subprocess
import sys

app = Flask(__name__)

def initialize_database():
    conn = sqlite3.connect('texts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS text_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT)''')
    conn.commit()
    conn.close()

def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/page2', methods=['GET', 'POST'])
def page2():
    if request.method == 'POST':
        text = request.form['Text']
        if text:
            conn = sqlite3.connect('texts.db')
            c = conn.cursor()
            c.execute("INSERT INTO text_data (text) VALUES (?)", (text,))
            conn.commit()
            conn.close()
            message = 'Text saved successfully!'
            return render_template('page2.html', message=message)
    return render_template('page2.html')

@app.route('/page3')
def page3():
    try:
        conn = sqlite3.connect('texts.db')
        c = conn.cursor()
        c.execute("SELECT * FROM text_data")
        texts = c.fetchall()
        conn.close()
    except sqlite3.Error as e:
        print("Error:", e)
        return "Error retrieving data from database."

    return render_template('page3.html', texts=texts)

@app.route('/clearupdatabase')
def clearupdatabase():
    return render_template('confirm.html')

@app.route('/clearupdatabase/confirm', methods=['POST'])
def clearupdatabase_confirm():
    if request.method == 'POST':
        if request.form['confirm'] == 'Yes':
            try:
                conn = sqlite3.connect('texts.db')
                c = conn.cursor()
                c.execute("DELETE FROM text_data")
                conn.commit()
                conn.close()
                message = 'Database cleared successfully!'
            except sqlite3.Error as e:
                print("Error:", e)
                message = 'Error clearing database.'
            return render_template('message.html', message=message)
        else:
            return render_template('index.html') 

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']

        if uploaded_file.filename != '':
            filename = uploaded_file.filename
            file_ext = os.path.splitext(filename)[1]
            unique_filename = str(uuid.uuid4()) + file_ext 
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            return f'File "{filename}" uploaded successfully!'
        else:
            return 'No file selected for upload.'
    else:
        return render_template('upload.html')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'Saves')

@app.route('/Storage')
def storage():
    return render_template('storage.html')

@app.route('/version')
def version():
    return render_template('version.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in
    logged_in = False

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'niggerbaby':
            logged_in = True
            return redirect('/manage')
        else:
            return render_template('auth.html', message='Login failed!')

    return render_template('auth.html')

@app.route('/logout')
def logout():
    logged_in = False
    return render_template('index.html')

@app.route('/manage')
def manage():
    if logged_in:
        return render_template('manage.html')
    else:
        return redirect('/login')

@app.route('/shell')
def shell():
    if logged_in:
        return render_template('shell.html')
    else:
        return redirect('/login')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error_404.html'), 404

if __name__ == '__main__':
    initialize_database()
    app.run(host="0.0.0.0", port=80, debug=True ,ssl_context=('certificate.pem' ,'key.key'))


