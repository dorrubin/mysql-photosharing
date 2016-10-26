'''
File: app.py
Author: Craig Einstein
'''

from flask import Flask, render_template, request
from flaskext.mysql import MySQL

app = Flask(__name__)


db = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'toor'
app.config['MYSQL_DATABASE_DB'] = 'sakila'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
db.init_app(app)

conn = db.connect()
cursor = conn.cursor()
query = 'Select title from film where film_id < 5;'

#Extracts data from a cursor
def extractData(cursor):
    data = []
    for item in cursor:
        data.append(item)
    return data

cursor.execute(query)
data = extractData(cursor)


#Page Definitions
@app.route('/', methods=['POST', 'GET'])
def index():
        return render_template('index.html', query=query, data=data)


@app.route('/search/')
def search():
    return render_template('search.html')


@app.route('/results/', methods=['POST', 'GET'])
def results():
    query = ''  # Empty string for query
    data = []  # Empty list for data
    if request.method == 'POST':  # If a post request is detected
        result = request.form  # Get form from request
        print(result)

        for key in result:  # iterate through the dictionary
            if key == 'Query':
                query = result[key]
        cursor = conn.cursor()
        #try query
        try:
            cursor.execute(query)
            return render_template('index.html', query=query, data=extractData(cursor))
        except:
            print("There is an error in the SQL syntax for: ", query)
            return render_template('index.html', query=query, error=1)
    else:  # If a get request is detected
        return render_template('index.html')
