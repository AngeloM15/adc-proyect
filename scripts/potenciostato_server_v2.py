import os
import sys
import argparse
import logging
import traceback
import json
import time

from datetime import datetime

#
import matplotlib.pyplot as plt
import seaborn as sns
#
HOME = os.path.expanduser('~')+"/potenciostato-project"

sys.path.append(f"{HOME}")

from libs.libdata import *
from libs.libutils import *


def main():
    """
    Main routine schedules the data gathering each period and process the data at the end
    """
    log.info("###### Starting Potenciostato Processing ######")

    # Libraries init
    log.debug("Init libraries")
    libutils = Libutils()
    libconversor = Libconversor()

    # Read potenciotato.json to get the time interval to process
    with open(f"{HOME}/config/potenciostato.json") as file:
        potenciotato_config = json.load(file)

    # Read config.json to get parameters of configuration
    with open(f"{HOME}/config/config.json") as file:
        config_json = json.load(file)
        sender_config = config_json["SENDER_PROCESS"]
        pot_config = config_json["POTENCIOSTATO_PROCESS"]

    # Set API
    libutils.set_channel(sender_config["CHANNEL_ID"],sender_config["WRITE_KEY"])

    # Set conversors
    libconversor.set_dac(potenciotato_config["DAC"])
    libconversor.set_adc()

    every = 60 # by default, sed every 1 minute

    # Variable to enable potenciotato mode
    potenciotato_mode = pot_config["ENABLE"]

    if potenciotato_mode:
        every = sender_config["PERIOD"]
        log.info("Potenciostato mode is enabled, will send every {} seconds".format(every))

    else:
        log.warning("No mode is enabled, will not process data")


    # Define data paths
    yearmonth = datetime.now().strftime('%Y-%m')
    libconversor.total_file_name = f"{HOME}/data/raw-data-{yearmonth}.csv"
    libconversor.temporal_file_name = f"{HOME}/data/tem-data-{yearmonth}.csv"

    if potenciotato_mode:

        # CLear temporal data
        libconversor.clear_data(libconversor.temporal_file_name)

        # Generate wave signal
        if libconversor.wave_type == "triangular":
            libconversor.triangular_wave()
        elif libconversor.wave_type == "square":
            libconversor.square_wave_v2()
        

        # Plot data
        libconversor.load_data(libconversor.temporal_file_name)
        log.info(f"\n{libconversor.signal_df}")
        df = libconversor.signal_df.iloc[::2]
        log.info(f"\n{df}")

        # Plot data
        sns.set(style="darkgrid", context = "paper", rc={'figure.figsize':(10,8)})
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

        sns.lineplot(data = df, x = df.index, y = "DAC", ax = ax1)
        sns.lineplot(data = df, x = df.index, y = "ADC", ax = ax2)

        plt.tight_layout()
        plt.show()

        sns.lineplot(data = df, x="DAC", y="ADC", sort=False, lw=1, estimator=None)
        plt.tight_layout()
        plt.show()

        # Send data
        for i,row in libconversor.signal_df.iterrows():
            libutils.write_data(row["DAC"],row["ADC"])
            time.sleep(every)

    else:
        log.warning("No mode is enabled, will not process data")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(add_help=False, description='Script for CounterParser processing')
    parser.add_argument( "--log-level", dest="loglevel", default=logging.INFO, \
                    type=lambda x: getattr(logging, x), help="Configure the logging level.", )
                    
    args = parser.parse_args()

    # create logger with 'main'
    log = logging.getLogger('main')
    log.setLevel(level=args.loglevel)
    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(level=args.loglevel)
    # create formatter and add it to the handlers
    if args.loglevel == 10: # DEBUG
        # %(filename)s:%(lineno)s
        formatter = logging.Formatter('%(asctime)s | %(levelname)7s | %(filename)s:%(funcName)5s:%(lineno)s | %(message)s')	
    else:
        formatter = logging.Formatter('%(asctime)s | %(levelname)7s | %(funcName)5s | %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    log.addHandler(ch)

    try:
        main()
    except Exception as e:
        log.error(f"Exception occurred during run: {e}")
        print(traceback.format_exc())
    finally:
        ts2 = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        log.info(f"Finishing... {ts2} ")