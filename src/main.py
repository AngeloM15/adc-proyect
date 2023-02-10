import argparse
import logging
import os
import sys
import time
import traceback
from datetime import datetime

import server
from tools.config import Api, Potenciostato

HOME = os.path.expanduser("~") + "/potenciostato-project"

sys.path.append(f"{HOME}")

from src.libdata import *


def main():
    """Main routine schedules the data gathering each period and process the data at the end"""

    log.info("###### Starting Potenciostato Processing ######")

    # Libraries init
    log.debug("Init libraries")

    # Initialize ThingSpeak API
    th_server = server.ThingSpeak()

    # Initialize comunnication with the device
    libconversor = Libconversor()

    every = 60  # by default, sed every 1 minute

    # Variable to enable potenciotato mode
    potenciotato_mode = Potenciostato.enable

    if potenciotato_mode:
        every = Api.delay
        log.info(
            "Potenciostato mode is enabled, will send every {} seconds".format(every)
        )

    else:
        log.warning("Mode is not enabled, will not process data")

    # Define data paths
    yearmonth = datetime.now().strftime("%Y-%m")
    libconversor.total_file_name = f"{HOME}/data/raw-data-{yearmonth}.csv"
    libconversor.temporal_file_name = f"{HOME}/data/tem-data-{yearmonth}.csv"

    if potenciotato_mode:

        # CLear temporal data
        libconversor.clear_data(libconversor.temporal_file_name)

        # Generate wave signal
        if Potenciostato.signal == "triangular":
            libconversor.triangular_wave()
        elif Potenciostato.signal == "square":
            libconversor.square_wave()

        # Plot data
        libconversor.load_data(libconversor.temporal_file_name)
        log.info(f"table:\n{libconversor.signal_df}")
        libconversor.plot_data(Potenciostato.signal, 5)

        # Send data
        for i, row in libconversor.signal_df.iterrows():
            th_server.write_data(row["DAC"], row["ADC"])
            time.sleep(every)

    else:
        log.warning("No mode is enabled, will not process data")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        add_help=False, description="Script for CounterParser processing"
    )
    parser.add_argument(
        "--log-level",
        dest="loglevel",
        default=logging.INFO,
        type=lambda x: getattr(logging, x),
        help="Configure the logging level.",
    )

    args = parser.parse_args()

    # create logger with 'main'
    log = logging.getLogger("main")
    log.setLevel(level=args.loglevel)
    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(level=args.loglevel)
    # create formatter and add it to the handlers
    if args.loglevel == 10:  # DEBUG
        # %(filename)s:%(lineno)s
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)7s | %(filename)s:%(funcName)5s:%(lineno)s | %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)7s | %(funcName)5s | %(message)s"
        )
    ch.setFormatter(formatter)
    # add the handlers to the logger
    log.addHandler(ch)

    try:
        main()
    except Exception as e:
        log.error(f"Exception occurred during run: {e}")
        print(traceback.format_exc())
    finally:
        ts2 = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log.info(f"Finishing... {ts2} ")
