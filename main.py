# all the imports
from flask import Flask, request, abort
from cross import crossdomain
import os
import json
import datetime
from entry import db, Entry

app = Flask(__name__)
app.config.from_object(__name__)

# load default config and override config from an environment variable
app.config.update(dict(
    #debug=True
    ))


@app.route("/highscore", methods=['get', 'post'])
@crossdomain(origin='*')
def handle_highscore():
    if request.method == "POST":
        score = request.form["score"]
        time = request.form["time"]
        return add_score(score, time)

    else:
        return return_top_ten()


def return_top_ten():
    scores = Entry.query.order_by(Entry.score.desc(), Entry.time.asc()).limit(10)
    jsonscores = []
    for entry in scores:
        jsonscores.append({"name": entry.name,
                           "score": entry.score,
                           "time": entry.time,
                           "datetime": str(entry.datetime)
                           })

    return json.dumps(jsonscores)


def add_score(score, time):
    try:
        score = int(score)
        time = float(time)
    except ValueError:
        return abort(400)
    entry = Entry(request.form['name'], request.form['score'], request.form['time'])
    db.session.add(entry)
    db.session.commit()
    return json.dumps({"highscore": True})


@app.route("/highscore/check", methods=["post"])
@crossdomain(origin="*")
def check_if_in_top_10():
    score = request.get['score']
    score = int(request.form["score"])
    time = int(request.form["time"])
    scores = Entry.query().order_by(Entry.score.desc(), Entry.time.asc()).limit(10)
    if len(scores) < 10:
        return json.dumps({"top10": True})
    highscore = 1000000000000000000
    hightime = 0
    for entry in scores:
        if entry.score < highscore:
            highscore = entry.score
            hightime = entry.time

    return json.dumps({"top10": (score > highscore or (score == highscore and hightime > time))
                       })


if __name__ == "__main__":
    app.debug = True
    app.run()
