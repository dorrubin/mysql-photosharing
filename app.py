# File: app.py
# Author: Dor Rubin

import flask
from flask import Flask, flash, Response, request, render_template, redirect, url_for
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
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config['UPLOAD_FOLDER'] = '/img'
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
    return flask.redirect(flask.url_for('hello'))


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
        cursor.execute("INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}','{6}' )".format(email, password, firstname, lastname, gender, dob, hometown))
        conn.commit()
        return flask.redirect(flask.url_for('login'))
    else:
        print("not unique user")
        return flask.redirect(flask.url_for('register', supress=True))


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def getUserEntryFromId(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE user_id = '{0}'".format(uid))
    return cursor.fetchone()


def isEmailUnique(email):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        #this means there are greater than zero entries with that email
        return False
    else:
        return True
#end login code


def areFriends(user_email, friend_email):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """SELECT *
               FROM Friends
               WHERE requester_email = '{0}'
               AND responder_email = '{1}'
               UNION
               SELECT *
               FROM Friends
               WHERE requester_email = '{1}'
               AND responder_email = '{0}'
            """.format(user_email, friend_email)
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data):
        result = True
    else:
        result = False
    return result  # 0 if not friends and 1 if yes

def ownsAlbum(uid, aid):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """ SELECT album_id
                FROM Album_User
                WHERE user_id = '{0}'
                AND album_id = '{1}';
            """.format(uid, aid)
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data):
        result = True
    else:
        result = False
    return result  # 0 if not friends and 1 if yes


def getAllAlbums():
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """ SELECT album_id, name
                FROM Albums;
            """
    cursor.execute(query)
    return cursor.fetchall()  # returns all user emails


def getUserAlbums(uid):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """ SELECT album_id, name
                FROM Albums NATURAL JOIN
                    (SELECT album_id
                    FROM Album_User
                    WHERE user_id = '{0}') AS T;
            """.format(uid)
    cursor.execute(query)
    return cursor.fetchall()  # returns all user emails

def getAlbumPhotos(aid):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """ SELECT *
                FROM Photos NATURAL JOIN
                    (SELECT photo_id
                    FROM Album_Photo
                    WHERE album_id = '{0}') AS T;
            """.format(aid)
    cursor.execute(query)
    return cursor.fetchall()  # returns all photos in that album

def getPhotoFromPhotoId(pid):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """ SELECT *
                FROM Photos
                WHERE photo_id = '{0}';
            """.format(pid)
    cursor.execute(query)
    return cursor.fetchall()[0]  # returns all photos in that album


@app.route('/profile', methods=['GET'])
@flask_login.login_required
def own_profile():
    user_id = flask_login.current_user.id
    return flask.redirect(flask.url_for('profile', page_id=user_id))


@app.route('/profile/<page_id>', methods=['GET', 'POST'])
@flask_login.login_required
def profile(page_id):
    if flask.request.method == 'GET':
        fname = getUserEntryFromId(page_id)[3]
        current_user = getUserEntryFromId(flask_login.current_user.id)[1]
        friend = getUserEntryFromId(page_id)[1]
        is_self = (flask_login.current_user.id == page_id)
        connection = areFriends(current_user, friend) or is_self
        user_albums = getUserAlbums(page_id)
        return render_template('profile.html', pageid=page_id, name=fname, friendship=connection, albums=user_albums)
    # POST Request
    looking_at = request.form.get('friendship')
    person_a = getUserEntryFromId(flask_login.current_user.id)[1]
    person_b = getUserEntryFromId(looking_at)[1]
    cursor.execute("INSERT INTO Friends (requester_email, responder_email) VALUES ('{0}', '{1}')".format(person_a, person_b))
    conn.commit()
    return flask.redirect(flask.url_for('friends'))


@app.route('/albums/<page_id>', methods=['GET'])
def albums(page_id):
    if flask.request.method == 'GET':
        user_id = 0
        if not flask_login.current_user.is_anonymous:
            user_id = flask_login.current_user.id
        album_owner = ownsAlbum(user_id, page_id)
        album_photos = getAlbumPhotos(page_id)
        return render_template('albums.html', pageid=page_id, photos=album_photos, owner=album_owner)

@app.route('/albums/<page_id>', methods=['POST'])
def delete_album(page_id):
    if flask.request.method == 'POST':
        album_id = request.form.get('album_deletion')
        user_id = 0
        if not flask_login.current_user.is_anonymous:
            user_id = flask_login.current_user.id
        cursor = conn.cursor()
        # get user email of users who are not friends with the logged in user
        query = """ DELETE
                    FROM Albums
                    WHERE album_id = '{0}';
                """.format(album_id)
        cursor.execute(query)
        conn.commit()
    return flask.redirect(flask.url_for('profile', page_id=user_id))


def getCommentsFromPhotoId(pid):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """ SELECT comment, first_name, last_name
                FROM Interactions NATURAL JOIN
                    (SELECT *
                    FROM Users) AS T
                WHERE photo_id = '{0}'
                AND comment IS NOT NULL;
            """.format(pid)
    cursor.execute(query)
    return cursor.fetchall()  # returns all photos in that album

def getTagsFromPhotoId(pid):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """ SELECT word
                FROM Photo_Tag
                WHERE photo_id = '{0}'
            """.format(pid)
    cursor.execute(query)
    return cursor.fetchall()  # returns all photos in that album

@app.route('/albums/<album_id>/photos/<photo_id>', methods=['GET'])
def photos(album_id, photo_id):
    if flask.request.method == 'GET':
        user_id = 1
        if not flask_login.current_user.is_anonymous:
            user_id = flask_login.current_user.id
        album_owner = ownsAlbum(user_id, album_id)
        user_photo = getPhotoFromPhotoId(photo_id)
        all_comments = getCommentsFromPhotoId(photo_id)
        all_tags = getTagsFromPhotoId(photo_id)
        return render_template('photo.html', photo=user_photo, owner=album_owner, comments=all_comments, tags=all_tags)

@app.route('/albums/<album_id>/photos/<photo_id>', methods=['POST'])
def interact_photo(album_id, photo_id):
    user_id = 1
    if not flask_login.current_user.is_anonymous:
        user_id = flask_login.current_user.id
    delete_photo_id = request.form.get('photo_deletion')
    like_photo_id = request.form.get('photo_like')
    comment_photo_id = request.form.get('pid')
    tag_photo_id = request.form.get('photo_tag')
    if delete_photo_id:
        cursor = conn.cursor()
        # get user email of users who are not friends with the logged in user
        query = """ DELETE
                    FROM Photos
                    WHERE photo_id = '{0}';
                """.format(delete_photo_id)
        cursor.execute(query)
        conn.commit()
        return flask.redirect(flask.url_for('albums', page_id=album_id))
    elif like_photo_id:
        cursor = conn.cursor()
        query = """ UPDATE Photos
                    SET likes = likes + 1
                    WHERE photo_id = '{0}';
                """.format(like_photo_id)
        cursor.execute(query)
        conn.commit()
        # update interactivity
        cursor = conn.cursor()
        query = """ INSERT INTO Interactions (user_id, photo_id, likes)
                    VALUES ("{0}", "{1}", "{2}");
                """.format(user_id, like_photo_id, 1)
        cursor.execute(query)
        conn.commit()
        return flask.redirect(flask.url_for('photos', album_id=album_id, photo_id=like_photo_id))
    elif comment_photo_id:
        comment = request.form.get('comment')
        # update interactivity
        cursor = conn.cursor()
        query = """ INSERT INTO Interactions (user_id, photo_id, comment)
                    VALUES ("{0}", "{1}", "{2}");
                """.format(user_id, comment_photo_id, comment)
        cursor.execute(query)
        conn.commit()
        return flask.redirect(flask.url_for('photos', album_id=album_id, photo_id=comment_photo_id))
    elif tag_photo_id:
        raw_tags = request.form.get('tag')
        tags = raw_tags.split()
        for tag in tags:
            addTagToTable(tag)
            connectTagToPhoto(tag_photo_id, tag)
        return flask.redirect(flask.url_for('photos', album_id=album_id, photo_id=tag_photo_id))


def connectTagToPhoto(pid, tag):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = ''' INSERT IGNORE INTO Photo_Tag(photo_id, word)
                VALUES ("{0}", "{1}")
            '''.format(pid, tag)
    cursor.execute(query)
    conn.commit()


def addTagToTable(tag):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = ''' INSERT IGNORE INTO Tags(word)
                VALUES ("{0}")
            '''.format(tag)
    cursor.execute(query)
    conn.commit()

def getAllUserFriends(email):
    cursor = conn.cursor()
    # get user email of users who are not friends with the logged in user
    query = """ SELECT user_id, email
                FROM Users NATURAL JOIN
                    (SELECT responder_email as email
                    FROM Friends
                    WHERE requester_email = '{0}'
                    UNION
                    SELECT requester_email as email
                    FROM Friends
                    WHERE responder_email = '{0}') AS T;
            """.format(email)
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


@app.route("/friends", methods=['GET'])
@flask_login.login_required
def friends():
    if flask.request.method == 'GET':
        email = getUserEntryFromId(flask_login.current_user.id)[1]
        friends = getAllUserFriends(email)
        other_users = getAllOtherUsers(flask_login.current_user.id)
        return render_template('friends.html', current_friends=friends, possible_friends=other_users)
    # else its a POST request

@app.route('/friends/search', methods=['GET', 'POST'])
def friend_search():
    if flask.request.method == 'GET':
        return render_template('search.html')
    #The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    #check if email is registered
    query = ''' SELECT user_id, email, first_name, last_name
                FROM Users
                WHERE email = '{0}'
            '''
    cursor.execute(query.format(email))
    data = cursor.fetchall()
    return render_template('search.html', search_friends=data)

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    # GET
    if flask.request.method == 'GET':
        user_albums = getUserAlbums(flask_login.current_user.id)
        return render_template('upload.html', albums=user_albums)
    # POST
    if 'in-imgdata' not in request.files:
        flash('no file part')
        return redirect(flask.url_for('upload_file'))
    file = request.files['in-imgdata']
    if file.filename == '':
        flash('no selected file')
        return redirect(flask.url_for('upload_file'))
    if file and allowed_file(file.filename):
        imgfile = request.files['in-imgdata']
        photo_data = base64.standard_b64encode(imgfile.read())
        user_id = flask_login.current_user.id
        album_id = request.form.get('in-album')
        if album_id == 'new':
            # create a new album first
            album_name = request.form.get('in-new-album-name')
            query = ''' INSERT INTO Albums(name)
                        VALUES ("{0}")
                    '''
            cursor = conn.cursor()
            cursor.execute(query.format(album_name))
            conn.commit()
            cursor = conn.cursor()
            cursor.execute("SELECT LAST_INSERT_ID();")
            album_id = cursor.fetchall()[0][0]
            query = ''' INSERT INTO Album_User(album_id, user_id)
                        VALUES ("{0}", "{1}")
                    '''
            cursor = conn.cursor()
            cursor.execute(query.format(album_id, user_id))
            conn.commit()
            # end if
        caption = request.form.get('in-caption')
        cursor = conn.cursor()
        query = ''' INSERT INTO Photos (imgdata, caption)
                    VALUES ("{0}", "{1}");
                '''
        cursor.execute(query.format(photo_data, caption))
        conn.commit()
        cursor.execute("SELECT LAST_INSERT_ID();")
        photo_id = cursor.fetchall()[0][0]
        cursor.execute("INSERT INTO Album_Photo (album_id, photo_id) VALUES ('{0}', '{1}' )".format(album_id, photo_id))
        conn.commit()
        return flask.redirect(flask.url_for('profile', page_id=user_id))
    #The method is POST

#end photo uploading code


def getTopTen():
    cursor = conn.cursor()
    query = """ SELECT email, count(likes), count(comment), count(interaction_id)
                FROM Interactions NATURAL JOIN
                    (SELECT *
                    FROM Users) AS T
                GROUP BY user_id
                ORDER BY count(interaction_id) DESC
                LIMIT 10;
            """
    cursor.execute(query)
    return cursor.fetchall()  # returns top 10 users


@app.route("/statistics", methods=['GET'])
def stats():
    ordered_ten = getTopTen()
    return render_template('stats.html', ranking=ordered_ten)


def getMostPopularTags():
    cursor = conn.cursor()
    query = """ SELECT word, count(word)
                FROM Photo_Tag
                GROUP BY word
                ORDER BY count(word) DESC
                LIMIT 5;
            """
    cursor.execute(query)
    return cursor.fetchall()  # returns top 10 users


def getPhotosFromMultipleTags(tags):
    cursor = conn.cursor()
    list_tags = tags.split('+')
    queries = []
    for i in range(len(list_tags)):
        # get user email of users who are not friends with the logged in user
        temp = """  (SELECT photo_id
                    FROM Photo_Tag
                    WHERE word = '{0}')
                """.format(list_tags[i])
        queries.append(temp)
    #end for
    middle = 'UNION ALL \n'.join(queries)
    query = """ SELECT *
                FROM Photos NATURAL JOIN
                (SELECT DISTINCT photo_id FROM(
                    {0}
                ) AS C) AS D;
            """.format(middle)
    cursor.execute(query)
    return cursor.fetchall()

@app.route('/tags', methods=['GET', 'POST'])
def tags():
    if flask.request.method == 'GET':
        most_popular = getMostPopularTags()
        return render_template('tags.html', top_tags=most_popular)
    raw_tags = flask.request.form['tag_search']
    list_tags = raw_tags.split()
    tags = '+'.join(list_tags)
    return flask.redirect(flask.url_for('specific_tag', page_id=tags))


@app.route('/tags/<page_id>', methods=['GET'])
def specific_tag(page_id):
    if flask.request.method == 'GET':
        tagged_photos = getPhotosFromMultipleTags(page_id)
        return render_template('tags.html', pageid=page_id, photos=tagged_photos)


def getRecoFromMultipleTags(tags):
    cursor = conn.cursor()
    list_tags = tags.split('+')
    queries = []
    for i in range(len(list_tags)):
        # get user email of users who are not friends with the logged in user
        temp = """  (SELECT photo_id
                    FROM Photo_Tag
                    WHERE word = '{0}')
                """.format(list_tags[i])
        queries.append(temp)
    #end for
    middle = 'UNION \n'.join(queries)
    query = """ SELECT word, count(word)
                FROM Photo_Tag NATURAL JOIN
                (SELECT DISTINCT photo_id FROM(
                    {0}
                ) AS C) AS D
                GROUP BY word
                ORDER BY count(word) DESC;
                LIMIT 5;
            """.format(middle)
    cursor.execute(query)
    return cursor.fetchall()

@app.route('/recommendations', methods=['GET', 'POST'])
def reco():
    if flask.request.method == 'GET':
        return render_template('recommendations.html')
    raw_tags = flask.request.form['tag_reco']
    list_tags = raw_tags.split()
    tags = '+'.join(list_tags)
    user_reco = getRecoFromMultipleTags(tags)
    return render_template('recommendations.html', recos=user_reco)


@app.route("/", methods=['GET'])
def hello():
    all_albums = getAllAlbums()
    return render_template('hello.html', albums=all_albums)


if __name__ == "__main__":
    #this is invoked when in the shell  you run
    #$ python app.py
    app.run(port=5000)
