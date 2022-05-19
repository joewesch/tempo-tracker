import sys
from datetime import datetime, date, timedelta

from prettytable import PrettyTable

from get_tempo import get_context


def main(args):
    # Default start date is yesterday
    end_date = date.today() - timedelta(days=1)
    if args:
        try:
            end_date = datetime.strptime(args[0], "%Y-%m-%d").date()
        except Exception as err:
            print(f"Unable to parse date: {err}")
    context = get_context(end_date)
    print(f"End Date: {end_date}")
    print(
        "== Week ==\n"
        f"Total Hours Expected: {context['week_denominator']}\n"
        f"Total Hours Recorded: {context['total_week_hours']} ({context['total_week_wellness']} Wellness)\n"
        f"Billable Hours: {context['total_week_billable']}\n"
        f"Billable Percentage: {(context['total_week_billable'] / (context['week_denominator'] - context['total_week_wellness']) * 100) if context['total_week_hours'] else 0:0.2f}%\n\n"
        "== Month ==\n"
        f"Total Hours Expected: {context['month_denominator']}\n"
        f"Total Hours Recorded: {context['total_month_hours']} ({context['total_month_wellness']} Wellness)\n"
        f"Billable Hours: {context['total_month_billable']}\n"
        f"Billable Percentage: {(context['total_month_billable'] / (context['month_denominator'] - context['total_month_wellness']) * 100) if context['total_month_hours'] else 0:0.2f}%\n\n"
        "== Quarter ==\n"
        f"Total Hours Expected: {context['quarter_denominator']}\n"
        f"Total Hours Recorded: {context['total_quarter_hours']} ({context['total_quarter_wellness']} Wellness)\n"
        f"Billable Hours: {context['total_quarter_billable']}\n"
        f"Billable Percentage: {(context['total_quarter_billable'] / (context['quarter_denominator'] - context['total_quarter_wellness']) * 100) if context['total_quarter_hours'] else 0:0.2f}%\n\n"
        "== Year ==\n"
        f"Total Hours Expected: {context['year_denominator']}\n"
        f"Total Hours Recorded: {context['total_year_hours']} ({context['total_year_wellness']} Wellness)\n"
        f"Billable Hours: {context['total_year_billable']}\n"
        f"Billable Percentage: {(context['total_year_billable'] / (context['year_denominator'] - context['total_year_wellness']) * 100) if context['total_year_hours'] else 0:0.2f}%\n"
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
