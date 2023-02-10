import json
import os
import sys
import time
from datetime import datetime

HOME = os.path.expanduser("~") + "/potenciostato-project"

sys.path.append(f"{HOME}")

from libs.libdata import *
from libs.libutils import *


def main():

    libutils = Libutils()
    libconversor = Libconversor()

    # Read config.json to get parameters of configuration
    with open(f"{HOME}/config/config.json") as file:
        config_json = json.load(file)
        sender_config = config_json["SENDER_PROCESS"]

    # Set API
    libutils.set_channel(sender_config["CHANNEL_ID"], sender_config["WRITE_KEY"])

    # Set period
    every = sender_config["PERIOD"]

    # Define data paths
    yearmonth = datetime.now().strftime("%Y-%m")
    libconversor.temporal_file_name = f"{HOME}/data/tem-data-{yearmonth}.csv"
    libconversor.load_data(libconversor.temporal_file_name)

    # Send data
    for i, row in libconversor.signal_df.iterrows():
        # libutils.write_data(row["DAC"],row["ADC"])
        print(row)
        time.sleep(every)


if __name__ == "__main__":
    main()
