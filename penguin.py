#!/usr/bin/env python
import sqlite3
import subprocess
import platform
from random import randint
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

def genpass(t):
	f = open('/usr/share/dict/words','r')
	dct = f.readlines()
	f.close()
	password = dct[randint(0,len(dct))].rstrip()
	if int(t) > 0:
		password = password + "-" + str(randint(0,9999))
		for i in xrange(t-1):
			password = password + "-" + dct[randint(0,len(dct))].rstrip()
	return password

def checkstatus():
	f = open('penguin.status','r')
	status = f.read().rstrip()
	if status == "complete":
		return False
	else:
		return True

# config

DATABASE = './penguin.db'
DEBUG = True
skey = "whoop"
username = "bob"
password = "bob"
complexity = "easy"
launcher = "./launch.sh"
update_status = "./stat.sh"

app = Flask(__name__)
app.secret_key = 'setecastronomy'
app.config.from_object(__name__)

@app.route('/')
def start():
	if checkstatus():
		return render_template('stage1.html')
	else:
		return render_template('setup.html')

@app.route('/stage2', methods=['POST'])
def stage2():
	if checkstatus():
		session['complexity']=request.form['complex']
		return render_template('stage2.html',complexity=session['complexity'],username=username,skey=skey,password=password)
	else:
		return render_template('setup.html')

@app.route('/stage3', methods=['POST'])
def stage3():
	if checkstatus():
		if session['complexity'] == 'easy':
			session['username'] = genpass(0)
			session['password'] = genpass(0)
			session['skey'] = genpass(2)
		else:
			session['username'] = str(request.form.get('username'))
			session['password'] = str(request.form.get('password'))
			session['skey'] = str(request.form.get('skey'))
		subprocess.Popen(["./launch.sh", session['username'],session['password'],session['skey']])
		return render_template('stage3.html')
	else:
		return render_template('setup.html')

@app.route('/complete')
def complete():
	if checkstatus():
		username = session['username']
		password = session['password']
		skey = session['skey']
		hostname = platform.node()
		subprocess.Popen([update_status])
		return render_template('complete.html',username=username,password=password,skey=skey,hostname=hostname)
	else:
		return render_template('setup.html')

if __name__ == '__main__':
	app.run()
