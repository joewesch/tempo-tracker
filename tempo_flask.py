from datetime import datetime, date

from flask import Flask, render_template, abort

from get_tempo import get_context

app = Flask(__name__)


@app.route("/")
def index():
    today = date.today()
    context = get_context(today)
    return render_template("index.html", **context)


# Deal with Chrome always attempting to find a favicon
@app.route("/favicon.ico")
def favicon():
    abort(404)


@app.route("/<path:path>")
def other_date(path):
    try:
        today = datetime.strptime(path, "%Y-%m-%d").date()
    except Exception as err:
        print(f"Unable to parse date: {err}")
        today = date.today()
    context = get_context(today)
    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
