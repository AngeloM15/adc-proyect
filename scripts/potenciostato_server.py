import os
import sys
import argparse
import logging
import asyncio
import traceback
import json
import time

from datetime import datetime

# HOME = os.path.expanduser('~')+"/git_test/adc-proyect"
HOME = os.path.expanduser('~')+"/potenciostato-project"

sys.path.append(f"{HOME}")

from libs.libdata import *
from libs.libutils import *


async def main(loop):
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

    # Set channel of the API
    libutils.set_channel(config_json["CHANNEL_ID"],config_json["WRITE_KEY"])
    
    # Set signal parameters
    libconversor.set_dac(potenciotato_config["ADC"])
    libconversor.set_adc()

    every = 1 # by default, process every 1 minutes

    # Variable to enable potenciotato mode
    potenciotato_mode = potenciotato_config["ENABLE"]

    if potenciotato_mode:
        every = potenciotato_config["PROCESS_PERIOD"]
        log.info("Potenciostato mode is enabled, will process every {} minutes".format(every))

    else:
        log.warning("No mode is enabled, will not process data")

    while True:
        """
        This performs every period in minutes
        """
        timeStmp = time.time()
        next_exec = every*60 - (int(timeStmp)%(every*60))
        log.info("Next execution in {} seconds".format(next_exec))
        await asyncio.sleep(next_exec)

        yearmonth = datetime.now().strftime('%Y-%m')
        libconversor.total_file_name = f"{HOME}/data/raw-data-{yearmonth}.csv"
        libconversor.temporal_file_name = f"{HOME}/data/tem-data-{yearmonth}.csv"
        # CLear data
        libconversor.clear_data(libconversor.temporal_file_name)

        if potenciotato_mode:

            # Generate signal
            libconversor.generate_signal()

            # Plot data
            libconversor.plot_data(libconversor.temporal_file_name)

            # # Send data
            # libutils.write_data(jsondata["sensors"]["DAC"],jsondata["sensors"]["ADC"])

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

    main_loop = asyncio.get_event_loop()
    try:
        tasks = [asyncio.ensure_future(main(main_loop))]
        main_loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as e:
        log.error(f"Exception occurred during run: {e}")
        print(traceback.format_exc())
    finally:
        ts2 = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        log.info(f"Finishing... {ts2} ")