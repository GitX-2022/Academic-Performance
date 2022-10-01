
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json
from fuzzy import compute_fuzzy

app = Flask(__name__)


app.secret_key = 'your secret key'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '*****'
app.config['MYSQL_DB'] = 'Academic_evaluation'


mysql = MySQL(app)


@app.route('/')

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM students WHERE roll_no = % s AND password = % s', (username, password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['roll_no']
			msg = 'Logged in successfully !'
			return render_template('index.html', msg = msg,account=account)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'roll_no' in request.form:
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		roll_no = request.form['roll_no']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM students WHERE roll_no = % s', (roll_no, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'name must contain only characters and numbers !'
		else:
			cursor.execute('INSERT INTO students VALUES (NULL, % s, % s, % s, % s)', (username, password, email, roll_no,))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

@app.route('/adminlogin', methods =['GET', 'POST'])
def adminlogin():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM admin WHERE username = % s AND password = % s', (username, password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			msg = 'Logged in successfully !'
			return render_template('admin.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('adminlogin.html', msg = msg)

@app.route("/index")
def index():
    if 'loggedin' in session:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM students WHERE id = % s', (session['id'], ))
            account = cursor.fetchone()
            return render_template("index.html", account = account)
    return redirect(url_for('login'))


@app.route("/adminindex")
def adminindex():
    if 'loggedin' in session:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM admin WHERE id = % s', (session['id'], ))
            account = cursor.fetchone()
            return render_template("admin.html", account = account)
    return redirect(url_for('login'))


@app.route("/display")
def display():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM students WHERE id = % s', (session['id'], ))
		account = cursor.fetchone()
		return render_template("display.html", account = account)
	return redirect(url_for('login'))

@app.route("/update", methods =['GET', 'POST'])
def update():
	msg = ''
	if 'loggedin' in session:
		if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'roll_no' in request.form:
			username = request.form['username']
			password = request.form['password']
			email = request.form['email']
			roll_no = request.form['roll_no']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT * FROM students WHERE roll_no = % s', (roll_no, ))
			account = cursor.fetchone()
			if account:
				msg = 'Account already exists !'
			elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
				msg = 'Invalid email address !'
			elif not re.match(r'[A-Za-z0-9]+', username):
				msg = 'name must contain only characters and numbers !'
			else:
				cursor.execute('UPDATE students SET name =% s, password =% s, email =% s, roll_no =% s WHERE id =% s', (username, password, email, roll_no, (session['id'], ), ))
				mysql.connection.commit()
				msg = 'You have successfully updated !'
		elif request.method == 'POST':
			msg = 'Please fill out the form !'
		return render_template("update.html", msg = msg)
	return redirect(url_for('login'))


@app.route("/displayperformance")
def display_performance():
    if 'loggedin' in session:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM students WHERE id = % s', (session['id'], ))
            account = cursor.fetchone()
            if account:
                cursor.execute('Select * from marks where roll_no = % s',(account['roll_no'],))
                msg = 'Viewing '+account['name']+ 'performance!'
                marks = cursor.fetchall()
                result_final = {}
                subjects =[] 
                value=[]
                for i in marks:
                    subjects.append(i['subject'])
                    att = int(i['attendance'])
                    int_mark = int(i['internal_mark'])
                    ext_mark = int(i['external_mark'])
                    result = compute_fuzzy(att, int_mark, ext_mark)
                    result_final[i['subject']] = round(float(result),2)
                    value.append(result)
            return render_template("display_performance.html", account = account,value=json.dumps(value),result_final=result_final,msg=msg,subjects=subjects)
    return redirect(url_for('login'))

@app.route("/add_marks", methods =['GET', 'POST'])
def add_marks():
	msg = ''
	if 'loggedin' in session:
            if request.method == 'POST' and 'roll_no' in request.form and 'subject' in request.form and 'internal_marks' in request.form and 'external_marks' in request.form :
                attendance = request.form['attendance']
                roll_no = request.form['roll_no']
                subject = request.form['subject']
                internal_marks = request.form['internal_marks']
                external_marks = request.form['external_marks']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM marks WHERE roll_no = % s and subject = %s', (roll_no,subject,))
                account = cursor.fetchone()
                if account:
                    msg = 'mark entry already done !'
                else:
                    cursor.execute('INSERT INTO marks VALUES (NULL, % s, % s, % s, % s,% s)', (roll_no, subject, internal_marks, external_marks,attendance))
                    mysql.connection.commit()
                    msg = 'You have successfully updated !'
            elif request.method == 'POST':
                msg = 'Please fill out the form !'
            return render_template("add_marks.html", msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
	app.run(host ="localhost", port = int("5001"))

