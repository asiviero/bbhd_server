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

@app.route("/user/<userid>", methods=["GET"])
def get_user(userid):
    cur = g.db.execute("select id, name, picture, fbid from user where id=%s" % userid)
    entries = [dict(id=str(row[0]), name=str(row[1]), picture=str(row[2]), fbid=str(row[3])) for row in cur.fetchall()]
    r = make_response( str(entries).replace("\'","\"") )
    r.mimetype = 'application/json'
    return r

@app.route("/user/", methods=["POST"])
def register_user():
    content_json = request.get_json()
    st = 'insert into user (name, fbid, picture) values ("%s", "%s", "%s")' % (content_json['name'], content_json['fbid'], content_json["picture"])
    g.db.execute(st)
    g.db.commit()
    print content_json
    return ""


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

    years = [2014,2015]
    for stat in map_stat_xpath:
        year = random.choice(years)
        print("%s: %s" % (stat, year))
        query_questions(stat,year)
        time.sleep(2)
    return ""
    # return str(query_questions("batting_average","2014"))

@app.route("/quiz/<quizid>/", methods=["GET"])
def get_quiz(quizid):
    cur = g.db.execute('select questions from quiz where id = %s' % int(quizid))
    entries = [dict(questions=str(row[0])) for row in cur.fetchall()]
    entries = entries[0]
    r = make_response( str(entries).replace("\'","\"").replace("\"[","[").replace("]\"","]") )
    r.mimetype = 'application/json'
    return r

@app.route("/generate_quiz/", methods=["POST"])
def generate_quiz():
    content_json = request.get_json()

    cur = g.db.execute('select title, correct_choice, time_limit, choices, id from question order by random() desc limit 9')
    entries = [dict(title=str(row[0]), correct=str(row[1]), time_limit=str(row[2]), choices=str(row[3]), id=str(row[4])) for row in cur.fetchall()]

    g.db.execute('insert into quiz (users, questions) values (?, ?)',
                 [content_json["users"], str(entries)])
    g.db.commit()

    cur = g.db.execute('select id from quiz order by id limit 1')
    entries_id = [row[0] for row in cur.fetchall()]
    quizid = entries_id[0]
    r_str = str({"id":quizid, "users": str(content_json["users"]), "questions": str(entries)}).replace("\'","\"").replace("\"[","[").replace("]\"","]")
    r = make_response( r_str )
    r.mimetype = 'application/json'
    return r

@app.route("/quiz_winner/<quizid>", methods=["PUT"])
def set_winner(quizid):
    content_json = request.get_json()
    g.db.execute('update quiz set winner = ? where id = ?',
                 [int(content_json["winner"]), int(quizid)])
    g.db.commit()

    cur = g.db.execute('select winner from quiz where id=%s' % quizid)
    entries_id = [row[0] for row in cur.fetchall()]
    winner = entries_id[0]
    r = make_response( str({"id": str(winner)}).replace("\'","\"") )
    r.mimetype = 'application/json'
    return r

@app.route("/answer_question/<quizid>", methods=["POST"])
def answer_question(quizid):
    content_json = request.get_json()
    user_id = content_json["user_id"]
    question_correct = content_json["question_correct"]
    question_index = content_json["question_index"]

    cur = g.db.execute('select users, user_1_right_answers, user_2_right_answers,user_1_indexes,user_2_indexes from quiz where id=%s' % quizid)
    entries_id = [{"user":row[0],"user_1_right_answers":row[1],"user_2_right_answers":row[2], "user_1_indexes":row[3], "user_2_indexes":row[4]} for row in cur.fetchall()]
    splitted = entries_id[0]["user"].split(",")

    if user_id == splitted[0]:
        field = "user_1_right_answers"
        field_index = "user_1_indexes"
        if question_correct:
            entries_id[0]["user_1_indexes"] += ", %s" % question_index
    else:
        field = "user_2_right_answers"
        field_index = "user_2_indexes"
        if question_correct:
            entries_id[0]["user_2_indexes"] += ", %s" % question_index

    g.db.execute('update quiz set %s = ?, %s="?" where id = ?' % (field,field_index),
                 [int(entries_id[0][field]) + 1*int(question_correct), entries_id[0][field_index], int(quizid)])
    g.db.commit()


@app.route("/end_quiz/<quizid>", methods=["POST"])
def end_quiz(quizid):

    cur = g.db.execute('select id, user_1_right_answers, user_2_right_answers, users from quiz where id=%s' % quizid)
    entries_id = [{"users":row[0],"user_1_right_answers":row[1],"user_2_right_answers":row[2],"user":row[3]} for row in cur.fetchall()]

    splitted = entries_id[0]["user"].split(",")

    if entries_id[0]["user_1_right_answers"] > entries_id[0]["user_2_right_answers"]:
        g.db.execute('update quiz set winner = ? where id = ?',
                     [splitted[0], int(quizid)])
        g.db.commit()
    else:
        g.db.execute('update quiz set winner = ? where id = ?',
                     [splitted[1], int(quizid)])
        g.db.commit()
    # think about this later








if __name__ == '__main__':
    app.debug = True
    app.run(host= '0.0.0.0')
