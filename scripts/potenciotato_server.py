import os
import argparse
import logging
import asyncio
import traceback
import json
import time

from datetime import datetime

HOME = os.path.expanduser('~')

async def main(loop):
    """
    Main routine schedules the data gathering each period and process the data at the end
    """
    log.info("###### Starting CounterParser Processing ######")

    # Libraries init
    log.debug("Init libraries")
    libutils = Libutils()
    libdata = Libdata()

    # Read potenciotato.json to get the time interval to process
    with open(f"{HOME}/config/potenciotato.json") as file:
        potenciotato_config = json.load(file)

    every = 1 # by default, process every 1 minutes

    # Variable to enable potenciotato mode
    potenciotato_mode = potenciotato_config["ENABLE"]

    if potenciotato_mode:
        every = potenciotato_config["PROCESS_PERIOD"]
        log.info("Raw mode is enabled, will process every {} minutes".format(every))

    else:
        log.warning("No mode is enabled, will not process data")

    # Frequency of the dataframe resample
    rule = '5T'

    while True:
        """
        This performs every period in minutes
        """
        timeStmp = time.time()
        next_exec = every*60 - (int(timeStmp)%(every*60))
        log.info("Next execution in {} seconds".format(next_exec))
        await asyncio.sleep(next_exec)

        yearmonth = datetime.now().strftime('%Y-%m')
        filename_generic_rawdata = HOME + '/oe-projects/data/generic-raw-data-' + yearmonth + '.csv'
        filename_generic_offdata = HOME + '/oe-projects/data/generic-offline-data-' + yearmonth + '.csv'
        filename_rawdata = HOME + '/oe-projects/data/piscari-occupation-raw-data-' + yearmonth + '.csv'

        if potenciotato_mode:
            # Get dataframe and mote list from CSV
            df_list, mote_list = get_df(filename_rawdata)

            for i, df in enumerate(df_list):

                # Get dataframe with occupacounter columns
                df_ocp = ocp_proccess(df)


                log.info("************** Occupacounter Dataframe of {} **************".format(mote_list[i]))
                log.debug("\n{}".format(df_ocp))

                # Only save the last 5 minutes
                log.info("************* Last {} minutes Dataframe *************".format(every))
                
                current_time = datetime.now()
                reference_time = current_time - timedelta(minutes = every)
                log.info("Get values since: {}".format(reference_time.strftime("%Y-%m-%d %H:%M:%S")))
                df_to_save = df_ocp.loc[reference_time:]
                log.debug("\n{}".format(df_to_save))

                if len(df_to_save):
                    
                    # Resample the data to be saved
                    log.info("**************** Dataframe Resampled ****************")
                    df_resampled = resample_df(df_to_save, rule)
                    log.debug("\n{}".format(df_resampled))

                    # Convert to a list of json objects
                    log.info("******************* JSON to save ********************")
                    list_json =json_convertor(df_resampled, mote_list[i])

                    for line in list_json:
                        # save data into file
                        libdata.savejsondata(filename_generic_rawdata, line)
                        libdata.savejsondata(filename_generic_offdata, line)
                log.info("==============================================================")
        
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