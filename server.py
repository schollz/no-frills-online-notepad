from flask import Flask, render_template, redirect, url_for, escape, request
from flask.ext.socketio import SocketIO, emit
from flaskext.mysql import MySQL
import json
from random import choice
from time import time

mysql = MySQL()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['MYSQL_DATABASE_USER'] = 'USER_NAME'
app.config['MYSQL_DATABASE_PASSWORD'] = 'PASSWORD'
app.config['MYSQL_DATABASE_DB'] = 'DB_NAME'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.debug = True
socketio = SocketIO(app)
mysql.init_app(app)

current_path = ""
animals = json.load(open('data/animals.json','r'))
adjs = json.load(open('data/adjectives.json','r'))
animal = {}

for a in animals:
	if a[0] not in animal:
		animal[a[0]] = []
	animal[a[0]].append(a)
	

@socketio.on('my event', namespace='/test')
def test_message(message):
	#message['data'] = escape(message['data'])
	print message
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT * from text where sitename='" + message['page'] + "' and version="+message['version'])
	data = cursor.fetchone()
	if data is None:
		print "Inserting into database"
		conn = mysql.connect()
		cursor = conn.cursor()
		query = '''INSERT INTO text (sitename,document,date_modified,date_created,version) VALUES (%s,%s,NOW(),NOW(),1)'''
		cursor.execute(query,(message['page'],message['data'],))
		conn.commit()
	else:
		currentSize = len(data[2])
		newSize = len(message['data'])
		currentVersion = int(data[5])
		if currentSize-newSize>10: # if deleting a lot of stuff, archive the old version
			print "archiving old version"
			currentVersion +=1
			conn = mysql.connect()
			cursor = conn.cursor()
			query = '''INSERT INTO text (sitename,document,date_modified,date_created,version) VALUES (%s,%s,NOW(),NOW(),%s)'''
			cursor.execute(query,(message['page'],message['data'],str(currentVersion),))
			conn.commit()
		else:
			print "updating into database, old version"
			conn = mysql.connect()
			cursor = conn.cursor()
			query = '''UPDATE text set document =%s, date_modified=NOW() where sitename=%s and version=%s'''
			cursor.execute(query,(message['data'],message['page'],str(currentVersion)))
			conn.commit()
		
	emit('newtitle', {'success':True,'data':'None'})

@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    print message['data']
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'success':True,'data': 'Connected'+current_path})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

@app.route('/')
def index():
	data = "already given"
	while data is not None:
		newName = choice(adjs)
		ani = choice(animal[newName[0]])
		newUrl = newName.title() + ani.title()
		newUrl = newUrl.replace('-','').replace("'",'').replace('"','').replace(' ','')
		cursor = mysql.connect().cursor()
		cursor.execute("SELECT * from text where sitename='" + newUrl + "'")
		data = cursor.fetchone()
	return redirect(newUrl)


@app.route('/<path:path>')
def catch_all(path):
	print path
	currentVersion = 1
	try:
		currentVersion = int(request.args.get('version', ''))
		current_path = path
		cursor = mysql.connect().cursor()
		cursor.execute("SELECT * from text where sitename='" + path + "' and version="+str(currentVersion))
		data = cursor.fetchone()
		document = ""
	except:
		cursor = mysql.connect().cursor()
		cursor.execute("SELECT * from text where sitename='" + path + "' order by version desc limit 1")
		data = cursor.fetchone()

		
	document = ""	
	if data is not None:
		document = data[2]
		currentVersion = int(data[5])
		
	return render_template('index.html',pagename=path,version=str(currentVersion),message="Start typing, it will save automatically.\nTo reload this note goto /"+path+"\nDo not post anything private, as anyone with the URL may be able to access it.",document=document)
		

if __name__ == '__main__':
    socketio.run(app,port=5000)
