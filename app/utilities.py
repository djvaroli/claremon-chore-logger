import os
import csv
from pathlib import Path
from datetime import datetime as dt


COLUMN_TITLES = ['Chore Name', 'Completed By', 'Date', 'Timestamp']


def write_log_entry_to_file(logs: dict):
    date_key = dt.now().strftime("%B-%d-%Y").lower()
    path_to_file = Path(f"chore_log_{date_key}.csv")

    mode = "w+"
    add_columns = False
    if os.path.exists(path_to_file) is False:
        mode = "a+"
        add_columns = True

    row = list(logs.values())
    with open(path_to_file, mode=mode) as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if add_columns:
            csv_writer.writerow(COLUMN_TITLES)

        csv_writer.writerow(row)
