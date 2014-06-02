# all the imports
import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify 
from cross import crossdomain
import json
import datetime

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'highscores.db'),
    DEBUG=True
    ))

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

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route("/highscore", methods=['GET', 'POST'])
@crossdomain(origin='*')
def handle_highscore():
    if request.method == "POST":
        score = request.form["score"]
        time = request.form["time"]
        return add_score(score, time)

    else:
        return return_top_ten()


def return_top_ten():
    db = get_db()
    cur = db.execute("""select name, score, time, datetime from highscore order by
            score desc, time asc limit 10""")
    scores = cur.fetchall()
    jsonscores = []
    for row in scores:
        jsonscores.append({"name": row["name"],
                           "score": row["score"],
                           "time": row["time"],
                           "datetime": row["datetime"]
                           })

    return json.dumps(jsonscores)

def add_score(score, time):
    try:
        score = int(score)
        time = float(time)
    except ValueError:
        return abort(400)
    parts = [request.form["name"], request.form["score"], request.form["time"], datetime.datetime.now()]
    db = get_db()
    values = db.execute('''insert into highscore (name, score, time, datetime) values (?, ?, ?, ?)''', parts)
    db.commit()
    newId = values.lastrowid
    allScores = db.execute('''select id from highscore order by score
                           desc limit 10''').fetchall()
    highscore = False
    for t in allScores:
        if newId in t:
            highscore = True
    return json.dumps({"highscore": highscore})


@app.route("/highscore/check", methods=["POST"])
@crossdomain(origin="*")
def check_if_in_top_10():
    # right now we are only checking for score 
    # not for the time. This needs fixing
    score = int(request.form["score"])
    time = int(request.form["time"])
    db = get_db()
    cur = db.execute("""select score, time from highscore order by
            score desc, time asc limit 10""")
    scores = cur.fetchall()
    if len(scores) < 10:
        return json.dumps({"top10" : True})
    highscore = 1000000000000000000
    hightime = 0
    for row in scores:
        if row["score"] < highscore:
            highscore = row["score"]
            hightime = row['time']

    return json.dumps({"top10": (score > highscore or (score == highscore and hightime > time))
                       })



if __name__ == "__main__":
    app.debug = True
    app.run()
