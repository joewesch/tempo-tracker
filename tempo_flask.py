from datetime import datetime, date, timedelta

from flask import Flask, render_template, abort

from get_tempo import get_context

app = Flask(__name__)


@app.route("/")
def index():
    # Default start date is yesterday
    end_date = date.today() - timedelta(days=1)
    context = get_context(end_date)
    context["end_date"] = str(end_date)
    return render_template("index.html", **context)


# Deal with Chrome always attempting to find a favicon
@app.route("/favicon.ico")
def favicon():
    abort(404)


@app.route("/<path:path>")
def other_date(path):
    try:
        end_date = datetime.strptime(path, "%Y-%m-%d").date()
    except Exception as err:
        print(f"Unable to parse date: {err}")
        # Default end date is yesterday
        end_date = date.today() - timedelta(days=1)
    context = get_context(end_date)
    context["end_date"] = str(end_date)
    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
