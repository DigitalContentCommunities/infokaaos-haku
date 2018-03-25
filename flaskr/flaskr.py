import os
import sqlite3
import json
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.route('/search', methods=['POST'])
def search():
    if request.form.get('search_word') == "":
        return "Search word empty!"
    db = get_db()
    search_word = request.form.get('search_word')
    splitti = search_word.split(",")
    splitti_query = ""
    for i in range(1, len(splitti)):
        splitti_query += ' or content like "%' + splitti[i] + '%" '
    query = 'select * from posts where content like "%'+ splitti[0] + '%"' + splitti_query + 'order by id desc'
    print(query)
    cur = db.execute('select * from posts where content like "%'+ splitti[0] + '%"' + splitti_query + 'order by id desc')
    entries = cur.fetchall()
    list = []
    for row in entries:
        list.append({"link": str(row['topic'].encode('utf-8'))})
    return json.dumps({"posts": list})
    return "Search executed"


@app.route('/')
def index():
    return render_template('frontend/index.html')

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)
