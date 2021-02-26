from flask import(
	Flask,
	render_template,
	redirect,
	url_for,
	session,
	request,
	flash
	)
from flask_mysqldb import MySQL
import MySQLdb.cursors
import string, re
import mysql.connector


app = Flask(__name__)

app.secret_key = "1234125135"
db_connect = mysql.connector.connect(user="root", password="cmpt276", host='127.0.0.1', port=3306, database='applogin')

@app.route("/")
def direct():
	return redirect(url_for('login'))

@app.route('/home')
def home():
	if 'logged_in' in session:
		return render_template('home.html', username = session['email'])
	return redirect(url_for('login'))


##pw is cmpt276 for db
@app.route('/login', methods=['POST', 'GET'])
def login():
	output = ''
	if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
		email = request.form['email']
		pwd= str(request.form['password'])
		# fetch info from database
		db_connect.ping(True)
		cursor = db_connect.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT ID, Email from accountinfo WHERE Email = %s AND password = %s', (email, pwd))
		account = cursor.fetchone()
		cursor.close()

		if account:
			(userId, email) = account
			session['logged_in'] = True
			session['id'] = userId
			session['email'] = email

			flash('Logged in successfully')
			return redirect(url_for('home'))
		else:
			output = 'Invalid User Credentials'

	return render_template('login.html', msg=output)

@app.route('/register', methods = ['GET', 'POST'])
def register():
	output = ''
	#Check if user submits form
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
		username = request.form['username']
		password = str(request.form['password'])
		email = request.form['email']

		db_connect.ping(True)
		cursor = db_connect.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accountinfo WHERE Email = %s', [email])
		account = cursor.fetchone()
		cursor.close()
		#check if email/account exist already exists
		if account:
			output = 'Account Already Exists'
		#check for valid email
		elif not ifValidEmail(email):
			output = 'Invalid Email Address'
		#check for valid username entry
		elif not ifValidUserName(username):
			output = 'Invalid Username (Must contain letters and numbers only!)'
		elif (len(password) < 5):
			output = 'Password must contain atleast 5 characters'
		elif not username or not password or not email:
			output = 'Please fill out the form!'
		else:
			#Create new Account
			db_connect.ping(True)
			cursor = db_connect.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('INSERT INTO accountinfo (username, password, Email, id) VALUES (%s, %s, %s,NULL)', (username, password, email,))
			db_connect.commit()
			cursor.close()
			output = 'You have successfully registered!'

			return redirect(url_for('login'))

	#Check if field is empty
	elif request.method == 'POST':
		output = 'Please fill the form to complete registration'


	return render_template('register.html', msg = output)


def ifValidUserName(username = ''):
	if not username:
		return 0
	else:
		if re.match("[A-Za-z0-9]+$", username):
			return True
		else:
			return False


def ifValidEmail(email = ''):
	if not email:
		return 0
	else:
		if re.match('[^@]+@[^@]+\.[^@]+', email):
			return True
		else:
			return False
