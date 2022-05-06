from datetime import datetime, date
from dateutil.relativedelta import MO, relativedelta
import os

from flask import Flask, render_template, request
import requests

app = Flask(__name__)


WELLNESS_CODES = ["NI2-5", "NI2-6", "NI2-22", "NI2-23"]

TEMPO_USER_ID = os.getenv("TEMPO_USER_ID")
if not TEMPO_USER_ID:
    raise ValueError("Missing environment variable TEMPO_USER_ID")

TEMPO_TOKEN = os.getenv("TEMPO_TOKEN")
if not TEMPO_TOKEN:
    raise ValueError("Missing environment variable TEMPO_TOKEN")


def get_entries(start, end):
    user_id = TEMPO_USER_ID
    token = TEMPO_TOKEN
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    url = f"https://api.tempo.io/core/3/worklogs/user/{user_id}"
    entries = []

    response = requests.get(
        url,
        headers=headers,
        params={
            "limit": "1000",  # Max page limit
            "from": start,
            "to": end,
        },
    )
    while True:
        jason = response.json()
        entries.extend(jason["results"])
        url = jason["metadata"].get("next")
        if not url:
            return entries
        response = requests.get(url, headers=headers)


def get_context(start_date):
    year_start = date(year=start_date.year, month=1, day=1)
    quarter_start = date(year=start_date.year, month=((2 + start_date.month) // 3) * 3 - 2, day=1)
    month_start = date(year=start_date.year, month=start_date.month, day=1)
    week_start = start_date + relativedelta(weekday=MO(-1))
    context = {
        "total_year_minutes": 0,
        "total_year_billable": 0,
        "total_year_wellness": 0,
        "total_quarter_minutes": 0,
        "total_quarter_billable": 0,
        "total_quarter_wellness": 0,
        "total_month_minutes": 0,
        "total_month_billable": 0,
        "total_month_wellness": 0,
        "total_week_minutes": 0,
        "total_week_billable": 0,
        "total_week_wellness": 0,
    }

    entries = get_entries(year_start.strftime("%Y-%m-%d"), start_date.strftime("%Y-%m-%d"))
    for entry in entries:
        entry_minutes = int(entry["timeSpentSeconds"] / 60)
        entry_billable = int(entry["billableSeconds"] / 60)
        context["total_year_billable"] += entry_billable
        if entry["issue"]["key"] not in WELLNESS_CODES:
            context["total_year_minutes"] += entry_minutes
        else:
            context["total_year_wellness"] += entry_minutes

        # if "QBR" in entry["description"] and "NI2-16" in entry["description"]:
        #     print(f"Possible QBR spotted: ({entry['startDate']}) {entry['description']}")
        entry_date = datetime.strptime(entry["startDate"], "%Y-%m-%d").date()
        if entry_date >= quarter_start:
            context["total_quarter_billable"] += entry_billable
            if entry["issue"]["key"] not in WELLNESS_CODES:
                context["total_quarter_minutes"] += entry_minutes
            else:
                context["total_quarter_wellness"] += entry_minutes
        if entry_date >= month_start:
            context["total_month_billable"] += entry_billable
            if entry["issue"]["key"] not in WELLNESS_CODES:
                context["total_month_minutes"] += entry_minutes
            else:
                context["total_month_wellness"] += entry_minutes
        if entry_date >= week_start:
            context["total_week_billable"] += entry_billable
            if entry["issue"]["key"] not in WELLNESS_CODES:
                context["total_week_minutes"] += entry_minutes
            else:
                context["total_week_wellness"] += entry_minutes

    return context


@app.route("/")
def index():
    today = date.today()
    context = get_context(today)
    return render_template("index.html", **context)


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
