import os
import yaml
import requests
import todocli
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


DATE_FORMAT = "%Y%m%d"


def check():
    # Check last time we checked for updates
    config_dir = "{}/.config/tod0".format(os.path.expanduser("~"))
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)

    last_update_check = datetime(1990, 1, 1)
    file_path = os.path.join(config_dir, "data.yml")
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            data = yaml.load(f, yaml.SafeLoader)
            if data and "last_update_check" in data:
                last_update_check = datetime.strptime(
                    data["last_update_check"], DATE_FORMAT
                )

    # Check for updates if it has been a day since last check
    if last_update_check + timedelta(days=1) < datetime.now():
        try:
            page = requests.get("https://pypi.org/simple/tod0/")
            soup = BeautifulSoup(page.text, features="html.parser")
            text_lines = soup.get_text().splitlines(keepends=False)

            # Look at the last 5 lines from the webpage
            for _line in text_lines[::-1][0:5]:
                if _line == "":
                    continue
                else:
                    latest_version = tuple(map(int, _line[5:10].split(".")))
                    break

            current_version = tuple(map(int, todocli.__version__.split(".")))

            if latest_version > current_version:
                print(
                    'Update available. You can update with "pip install --upgrade tod0"'
                )

            with open(file_path, "w") as f:
                yaml.dump(
                    {"last_update_check": datetime.now().strftime(DATE_FORMAT)}, f
                )
        except:
            print("Error getting update information")
