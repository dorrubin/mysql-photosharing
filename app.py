# File: app.py
# Author: Dor Rubin

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login as flask_login
# Testing
from IPython import embed

#for image uploading
from werkzeug import secure_filename
import os
import base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!
app.debug = True



#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'toor'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
# app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form></br>
           <a href='/'>Home</a>
               '''
    #The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    #check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.email = email
            user_id = getUserIdFromEmail(email)
            user.id = user_id
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('profile', page_id=user_id))

    #information did not match
    return "<a href='/login'>Try again</a>\
            </br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    get_suppress = request.args.get('supress')
    return render_template('register.html', supress=get_suppress)


@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        hometown = request.form.get('hometown')
    except:
        print("couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}','{6}' )".format(email, password, firstname, lastname, gender, dob, hometown)))
        conn.commit()
        #log user in
        # user = User()
        # user.email = email
        # user.id = getUserIdFromEmail(email)
        # user_id = user.id
        # flask_login.login_user(user)
        return flask.redirect(flask.url_for('login'))
    else:
        print("not unique user")
        return flask.redirect(flask.url_for('register', supress=True))


def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id FROM Pictures WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def getUserNameFromId(id):
    cursor = conn.cursor()
    cursor.execute("SELECT first_name  FROM Users WHERE user_id = '{0}'".format(id))
    return cursor.fetchone()[0]

def isEmailUnique(email):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        #this means there are greater than zero entries with that email
        return False
    else:
        return True
#end login code

@app.route('/profile')
@flask_login.login_required
def own_profile():
    user_id = flask_login.current_user.id
    return flask.redirect(flask.url_for('profile', page_id=user_id))

@app.route('/profile/<page_id>')
@flask_login.login_required
def profile(page_id):
    fname = getUserNameFromId(page_id)
    return render_template('profile.html', name=fname)

def getAllUserFriends(uid):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """SELECT responder_email
               FROM Friends
               WHERE requester_email = '{0}'
               UNION
               SELECT requester_email
               FROM Friends
               WHERE responder_email = '{0}'
            """.format(uid)
    cursor.execute(query)
    return cursor.fetchall()  # returns all user emails


def getAllOtherUsers(uid):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """SELECT email
               FROM Users AS U
               WHERE email != '{0}'
               NOT IN
               (SELECT responder_email
               FROM Friends
               WHERE requester_email = U.email
               UNION
               SELECT requester_email
               FROM Friends
               WHERE responder_email = U.email)
            """.format(uid)
    cursor.execute(query)
    return cursor.fetchall()  # returns all user emails


@app.route("/friends", methods=['GET', 'POST'])
@flask_login.login_required
def friends():
    friends = getAllUserFriends(flask_login.current_user.id)
    other_users = getAllOtherUsers(flask_login.current_user.id)
    return render_template('friends.html', message="Look at all your possible friends", current_friends=friends, possible_friends=other_users)


#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['file']
        photo_data = base64.standard_b64encode(imgfile.read())
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Pictures (imgdata, user_id) VALUES ('{0}', '{1}' )".format(photo_data, uid))
        conn.commit()
    return render_template('profile.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid))
    #The method is GET so we return a  HTML form to upload the a photo.
    return '''
        <!doctype html>
        <title>Upload new Picture</title>
        <h1>Upload new Picture</h1>
        <form action="" method=post enctype=multipart/form-data>
        <p><input type=file name=file>
        <input type=submit value=Upload>
        </form></br>
    <a href='/'>Home</a>
        '''
#end photo uploading code


#default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    #this is invoked when in the shell  you run
    #$ python app.py
    app.run(port=5000)
