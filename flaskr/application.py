from flask import Flask
import requests
import xml.etree.ElementTree as ET
import random
import time

# all the imports
import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, make_response

# configuration
DATABASE = os.path.dirname(os.path.realpath(__file__)) + '/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def hello_world():
    cur = g.db.execute('select title, correct_choice, time_limit, choices from question order by id desc')
    entries = [dict(title=row[0], correct=row[1], choices=row[3]) for row in cur.fetchall()]
    return str(entries)

@app.route("/fetch_questions/")
def fetch_questios():
    cur = g.db.execute('select title, correct_choice, time_limit, choices from question order by random() desc limit 9')
    entries = [dict(title=str(row[0]), correct=str(row[1]), choices=str(row[3])) for row in cur.fetchall()]
    r = make_response( str(entries).replace("\'","\"") )
    r.mimetype = 'application/json'
    return r
    # return jsonify(str(entries))

@app.route('/add', methods=['POST'])
def add_entry():
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('hello_world'))

map_stat_xpath = {
    "Home Runs" : "{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}hitting//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}home_runs//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}players//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}player",
    "Strikeouts" : "{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}pitching//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}strikeouts//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}players//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}player",
    "Games Saved" : "{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}pitching//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}games_saved//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}players//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}player",
    "Stolen Bases" : "{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}hitting//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}stolen_bases//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}players//{http://feed.elasticstats.com/schema/baseball/v5/leaders.xsd}player"
}

def query_questions(stat,year):
    full_data_url = "http://api.sportradar.us/mlb-t5/seasontd/%s/REG/leaders/statistics.xml?api_key=336as6g3h86kyqswae2g2c97" % (year,)
    r = requests.get(full_data_url)
    root = ET.fromstring(r.text)

    question_format = "Who had the most %s in %s?" % (stat,year)
    print(root.tag)
    #players = root.findall("home_runs")
    #print players
    # print root[0].attrib
    mlb = root[0]

    home_runs = mlb.findall(map_stat_xpath[stat])
    rank = [{"player": str(player.get("first_name") + " " + player.get("last_name")), "rank": int(player.get("rank"))} for player in home_runs]
    # print(rank)
    random.shuffle(rank)
    ranked_order = sorted(rank[:4], key=lambda k: k["rank"])
    choices = ", ".join([player["player"] for player in rank[:4]])
    correct = ranked_order[0]["player"]
    g.db.execute('insert into question (title, correct_choice, time_limit, choices) values (?, ?, ?, ?)',
                 [question_format, correct, 20, choices])
    g.db.commit()
    return ""


@app.route("/get_questions/", methods=['GET'])
def get_questions():

    years = range(1990,2014)
    years.remove(2012) # 2012 data is incomplete
    for stat in map_stat_xpath:
        year = random.choice(years)
        year = 2014
        print("%s: %s" % (stat, year))
        query_questions(stat,year)
        time.sleep(2)
    return ""
    # return str(query_questions("batting_average","2014"))









if __name__ == '__main__':
    app.debug = True
    app.run()
