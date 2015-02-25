from flask import Flask, request, abort, jsonify, json
from cross import crossdomain
import calendar
import datetime
from entry import db, Entry


app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/highscore", methods=['get', 'post', "options"])
@crossdomain(origin='*', headers="Content-Type")
def handle_highscore():
    if request.method == "POST":
        content = request.get_json()
        score = content["score"]
        time = content["time"]
        name = content["name"]
        return add_score(score, time, name)

    else:
        return return_top_ten()


def return_top_ten():
    all_scores = []

    sorted_months = sorted(get_all_months_with_entries(), key=lambda date_range: date_range[0])

    total_months = len(sorted_months)
    for i, monthrange in enumerate(sorted_months):
        scores_for_month = {}
        limit = 10 if (i == total_months - 1) else 3
        scores = Entry\
            .query\
            .filter(Entry.datetime <= monthrange[1], Entry.datetime >= monthrange[0])\
            .order_by(Entry.score.desc(), Entry.time.asc())\
            .limit(limit)
        scores_for_month["month"] = str(monthrange[0])
        scores_for_month["scores"] = create_json_scores(scores)
        all_scores.append(scores_for_month)

    all_scores.reverse()
    allTimeScores = Entry.query.order_by(Entry.score.desc(), Entry.time.asc()).limit(10)
    all_scores.append({"month": "allTime", "scores": create_json_scores(allTimeScores)})
    return json.dumps(all_scores)


def create_json_scores(entries):
    return [entry.to_json() for entry in entries]


def add_score(score, time, name):
    try:
        score = int(score)
        time = float(time)
    except ValueError:
        return abort(400)
    entry = Entry(name, score, time)
    db.session.add(entry)
    db.session.commit()
    return jsonify({'success': True})


def get_all_months_with_entries():
    values = Entry.query.all()
    all_dates = set([get_first_day_in_month(e.datetime) for e in values])
    month_ranges = [get_month_range(date) for date in all_dates]
    return month_ranges


def get_month_range(date):
    return [get_first_day_in_month(date), get_last_day_in_month(date)]


def get_last_day_in_month(date):
    return datetime.datetime(date.year, date.month, calendar.monthrange(date.year, date.month)[1], 23, 59, 59)


def get_first_day_in_month(date):
    return datetime.date(date.year, date.month, 1)


@app.route("/highscore/check", methods=["post", "options"])
@crossdomain(origin="*", headers="Content-Type")
def check_if_in_top_10():
    content = request.get_json()
    score = content["score"]
    time = content["time"]
    today = datetime.date.today()
    scores = Entry\
        .query\
        .filter(Entry.datetime <= get_last_day_in_month(today), Entry.datetime >= get_first_day_in_month(today))\
        .order_by(Entry.score.desc(), Entry.time.asc())\
        .limit(10)

    if scores.count() < 10:
        return jsonify({"top10": True})

    worst_entry_in_top_ten = min(scores, key=lambda score: score.score)

    return jsonify({"top10": (score > worst_entry_in_top_ten.score or (score == worst_entry_in_top_ten.score and worst_entry_in_top_ten.time > time))
                    })

if __name__ == "__main__":
    app.debug = True
    app.run()
