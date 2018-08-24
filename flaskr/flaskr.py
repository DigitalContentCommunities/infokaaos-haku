import os
import sqlite3
import json
import operator
import tempfile
from tempfile import NamedTemporaryFile
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

def get_category_dict():
    f = open("domain_subcategories.csv").read()
    dicti = {}
    for row in f.split("\n"):
        if row == "":
            continue
        domain = row.split(",")[0]
        cat = row.split(",")[1]
        if domain not in dicti:
            dicti[domain] = cat
    return dicti

def get_frequency_dict(domains):
    dicti = {}
    for item in domains:
        for word in item.split(" "):
            if not word.isspace() and word != "":
                if word in dicti:
                    dicti[word] = dicti[word] + 1
                else:
                    dicti[word] = 1
    return dicti

def get_class_dict(domain_dicti):
    class_dict = get_category_dict()
    class_freq_dict = {'not_found' : 0}
    for key in sorted(domain_dicti.keys()):
        value = domain_dicti[key]
        if key not in class_dict:
            class_freq_dict['not_found'] += value
            continue
        category = class_dict[key]
        if category in class_freq_dict:
            class_freq_dict[category] = class_freq_dict[category] + value
        else:
            class_freq_dict[category] = value
    print(class_freq_dict)
    return class_freq_dict

def get_media_counts(media_id_list):
    return_list = []
    return_list.append(str(media_id_list.count(1)))
    return_list.append(str(media_id_list.count(2)))
    return_list.append(str(media_id_list.count(3)))
    return_list.append(str(media_id_list.count(4)))
    return_list.append(str(media_id_list.count(5)))
    return_list.append(str(media_id_list.count(6)))
    return ",".join(return_list)

def get_domain_string(domainit):
    returni = ""
    for w in sorted(domainit.keys()):
        returni += w + "," + str(domainit[w]) + "\n"
    return returni

def get_class_string(class_dict):
    returni = ""
    all = ""
    for w in sorted(class_dict.keys()):
        returni += w + "," + str(class_dict[w]) + "</br>"
        all += str(class_dict[w]) + ","
    return returni + all

@app.route('/search', methods=['POST'])
def search():
    #if request.form.get('search_word') == "":
    #    return "Search word empty!"
    db = get_db()

    search_word = request.form.get('search_word')
    splitti = search_word.split(",")
    splitti_query = ""
    for i in range(1, len(splitti)):
        if len(splitti[i]) < 2:
            continue
        splitti_query += ' or content like "%' + splitti[i] + '%" '
    query = 'select * from posts where content like "%'+ splitti[0] + '%"' + splitti_query + ' and media_id != 5 and not date like "%2018%" order by id desc'
    print(query)
    cur = db.execute('select * from posts where content like "%'+ splitti[0] + '%"' + splitti_query + ' and media_id != 5 and not date like "%2018%" order by id desc')
    entries = cur.fetchall()

    list = []
    domain_list = []
    media_id_list = []
    links = []
    for row in entries:
        domain_list.append(str(row['topic'].encode('utf-8')))
        media_id_list.append(int(row['media_id']))
        links.append(str(row['link'].encode('utf-8')))
    domain_dicti = get_frequency_dict(domain_list)
    class_dict = get_class_dict(domain_dicti)
    print(class_dict)
    domainit = domain_dicti
    media_counts = get_media_counts(media_id_list)
    return json.dumps({"classes": get_class_string(class_dict), "domains": get_domain_string(domainit), "media_counts": str(media_counts), "links": "\n".join(links)})
    return "Search executed"


@app.route('/')
def index():
    return render_template('frontend/index.html')

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)
