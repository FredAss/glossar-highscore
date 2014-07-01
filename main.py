# all the imports
from flask import Flask, request, abort, jsonify
from cross import crossdomain
import calendar
from datetime import date, datetime
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
    allScores = {}

    for monthrange in get_all_months_with_entries():
        scores = Entry\
            .query\
            .filter(Entry.datetime <= monthrange[1], Entry.datetime >= monthrange[0])\
            .order_by(Entry.score.desc(), Entry.time.asc()).limit(10)
        allScores[str(monthrange[0])] = createJsonScores(scores)

    allTimeScores = Entry.query.order_by(Entry.score.desc(), Entry.time.asc()).limit(10)
    allScores['allTime'] = createJsonScores(allTimeScores)

    return jsonify(allScores)


def createJsonScores(entries):
    jsonscores = []
    for entry in entries:
        jsonscores.append({"name": entry.name,
                           "score": entry.score,
                           "time": entry.time,
                           "datetime": str(entry.datetime)
                           })
    return jsonscores


def add_score(score, time):
    try:
        score = int(score)
        time = float(time)
    except ValueError:
        return abort(400)
    entry = Entry(request.form['name'], request.form['score'], request.form['time'])
    db.session.add(entry)
    db.session.commit()
    return jsonify({'success': True})


def get_all_months_with_entries():
    values = Entry.query.all()
    l = set([getFirstDayInMonth(e.datetime) for e in values])
    l = [getMonthRange(m) for m in l]
    return l


def getMonthRange(d):
    return [date(d.year, d.month, 1), getLastDayInMonth(d)]


def getLastDayInMonth(d):
    return datetime(d.year, d.month, calendar.monthrange(d.year, d.month)[1], 23, 59, 59)


def getFirstDayInMonth(d):
    return date(d.year, d.month, 1)


@app.route("/highscore/check", methods=["post"])
@crossdomain(origin="*")
def check_if_in_top_10():
    score = int(request.form["score"])
    time = int(request.form["time"])
    today = date.today()
    scores = Entry\
        .query\
        .filter(Entry.datetime <= getLastDayInMonth(today), Entry.datetime >= getFirstDayInMonth(today))\
        .order_by(Entry.score.desc(), Entry.time.asc()).limit(10)
    if scores.count() < 10:
        return jsonify({"top10": True})
    highscore = 1000000000000000000
    hightime = 0
    for entry in scores:
        if entry.score < highscore:
            highscore = entry.score
            hightime = entry.time

    return jsonify({"top10": (score > highscore or (score == highscore and hightime > time))
                    })


if __name__ == "__main__":
    app.debug = True
    app.run()
