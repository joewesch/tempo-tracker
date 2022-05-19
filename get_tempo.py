from datetime import datetime, date, timedelta
from dateutil.relativedelta import MO, relativedelta
import os

import requests
import numpy


WELLNESS_CODES = ["NI2-5", "NI2-6", "NI2-22", "NI2-23"]

# These are codes that show up in Tempo as billable, but they shouldn't be
NON_BILLABLE_CODES = ["NI2-18", "NAUTOBOT-269", "NAUTOBOT-270", "NAUTOBOT-391", "NAUTOBOT-392"]

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


def get_context(end_date):
    year_start = date(year=end_date.year, month=1, day=1)
    quarter_start = date(year=end_date.year, month=((2 + end_date.month) // 3) * 3 - 2, day=1)
    month_start = date(year=end_date.year, month=end_date.month, day=1)
    week_start = end_date + relativedelta(weekday=MO(-1))
    # numpy.busday_count is not inclusive for the end date, so this adds an additional day
    end_plus_one = end_date + timedelta(days=1)
    context = {
        "year_denominator": numpy.busday_count(year_start, end_plus_one) * 8,
        "quarter_denominator": numpy.busday_count(quarter_start, end_plus_one) * 8,
        "month_denominator": numpy.busday_count(month_start, end_plus_one) * 8,
        "week_denominator": numpy.busday_count(week_start, end_plus_one) * 8,
        "total_year_hours": 0,
        "total_year_billable": 0,
        "total_year_wellness": 0,
        "total_quarter_hours": 0,
        "total_quarter_billable": 0,
        "total_quarter_wellness": 0,
        "total_month_hours": 0,
        "total_month_billable": 0,
        "total_month_wellness": 0,
        "total_week_hours": 0,
        "total_week_billable": 0,
        "total_week_wellness": 0,
        "weeks": {},
    }

    entries = get_entries(year_start.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    for entry in entries:
        entry_hours = float(entry["timeSpentSeconds"] / 3600)
        entry_billable = float(entry["billableSeconds"] / 3600)
        if entry["issue"]["key"] in NON_BILLABLE_CODES:
            entry_billable = 0.0
        context["total_year_billable"] += entry_billable
        if entry["issue"]["key"] not in WELLNESS_CODES:
            context["total_year_hours"] += entry_hours
        else:
            context["total_year_wellness"] += entry_hours

        # if "QBR" in entry["description"] and "NI2-16" in entry["description"]:
        #     print(f"Possible QBR spotted: ({entry['startDate']}) {entry['description']}")
        entry_date = datetime.strptime(entry["startDate"], "%Y-%m-%d").date()
        week_num = entry_date.isocalendar().week
        context["weeks"].setdefault(
            week_num,
            {
                "start_date": str(entry_date),
                "total": 0,
                "billable": 0,
                "nonbillable": 0,
                "well": 0,
            },
        )
        context["weeks"][week_num]["total"] += entry_hours
        if entry_billable:
            context["weeks"][week_num]["billable"] += entry_billable
        elif entry["issue"]["key"] in WELLNESS_CODES:
            context["weeks"][week_num]["well"] += entry_hours
        else:
            context["weeks"][week_num]["nonbillable"] += entry_hours

        if entry_date >= quarter_start:
            context["total_quarter_billable"] += entry_billable
            if entry["issue"]["key"] not in WELLNESS_CODES:
                context["total_quarter_hours"] += entry_hours
            else:
                context["total_quarter_wellness"] += entry_hours
        if entry_date >= month_start:
            context["total_month_billable"] += entry_billable
            if entry["issue"]["key"] not in WELLNESS_CODES:
                context["total_month_hours"] += entry_hours
            else:
                context["total_month_wellness"] += entry_hours
        if entry_date >= week_start:
            context["total_week_billable"] += entry_billable
            if entry["issue"]["key"] not in WELLNESS_CODES:
                context["total_week_hours"] += entry_hours
            else:
                context["total_week_wellness"] += entry_hours

    return context
