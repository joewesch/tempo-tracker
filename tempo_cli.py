import sys
from datetime import datetime, date

from prettytable import PrettyTable

from get_tempo import get_context


def main(args):
    today = date.today()
    if args:
        try:
            today = datetime.strptime(args[0], "%Y-%m-%d").date()
        except Exception as err:
            print(f"Unable to parse date: {err}")
    context = get_context(today)
    print(
        "== Week ==\n"
        f"Total Minutes: {context['total_week_minutes']} ({context['total_week_wellness']} Wellness)\n"
        f"Billable Minutes: {context['total_week_billable']}\n"
        f"Billable Percentage: {(context['total_week_billable'] / context['total_week_minutes'] * 100) if context['total_week_minutes'] else 0:0.2f}%\n\n"
        "== Month ==\n"
        f"Total Minutes: {context['total_month_minutes']} ({context['total_month_wellness']} Wellness)\n"
        f"Billable Minutes: {context['total_month_billable']}\n"
        f"Billable Percentage: {(context['total_month_billable'] / context['total_month_minutes'] * 100) if context['total_month_minutes'] else 0:0.2f}%\n\n"
        "== Quarter ==\n"
        f"Total Minutes: {context['total_quarter_minutes']} ({context['total_quarter_wellness']} Wellness)\n"
        f"Billable Minutes: {context['total_quarter_billable']}\n"
        f"Billable Percentage: {(context['total_quarter_billable'] / context['total_quarter_minutes'] * 100) if context['total_quarter_minutes'] else 0:0.2f}%\n\n"
        "== Year ==\n"
        f"Total Minutes: {context['total_year_minutes']} ({context['total_year_wellness']} Wellness)\n"
        f"Billable Minutes: {context['total_year_billable']}\n"
        f"Billable Percentage: {(context['total_year_billable'] / context['total_year_minutes'] * 100) if context['total_year_minutes'] else 0:0.2f}%\n"
    )
    table = PrettyTable()
    table.field_names = ["Week Start", "Total", "Billable", "Non-Billable", "Wellness"]
    table.align["Total"] = "r"
    table.align["Billable"] = "r"
    table.align["Non-Billable"] = "r"
    table.align["Wellness"] = "r"
    for week in context["weeks"].values():
        table.add_row(
            [
                week["start_date"],
                week["total"],
                week["billable"],
                week["nonbillable"],
                week["well"],
            ]
        )
    print("== Weekly Breakdown ==")
    print(table)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
