import os
import csv
from pathlib import Path
from datetime import datetime as dt


COLUMN_TITLES = ['Chore Name', 'Completed By', 'Date', 'Timestamp']


def get_now_date_key():
    return dt.now().strftime("%B-%d-%Y").lower()


def write_log_entry_to_file(
        chore_name: str,
        completed_by: str,
        date: str,
        timestamp: int,
        path_to_file: str = "claremon_chore_logs.csv"
) -> int:
    mode = "w+"
    add_columns = False
    if os.path.exists(path_to_file) is False:
        mode = "a+"
        add_columns = True

    row = [chore_name, completed_by, date, timestamp]
    with open(path_to_file, mode=mode) as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if add_columns:
            csv_writer.writerow(COLUMN_TITLES)

        csv_writer.writerow(row)

    return 1
