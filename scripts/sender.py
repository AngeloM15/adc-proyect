import os
import sys
import thingspeak
import pandas as pd
import time
from datetime import datetime

HOME = os.path.expanduser("~")
sys.path.append(f"{HOME}/git_test/adc-proyect")

from libs.libdata import *

channel_id = 1771605 # PUT CHANNEL ID HERE
write_key  = 'TL2SQ8QAKQ2UMSPF' # PUT YOUR WRITE KEY HERE
read_key   = 'YELTAF76LQZ3SNCN' # PUT YOUR READ KEY HERE

libdata = Libdata()


def measure(channel):
    try:
        adc,dac = libdata.get_data()

        # write
        response = channel.update({'field1': adc, 'field2': dac})

        # read
        read = channel.get({})
        print("Read:", read)

    except Exception as e:
        print(e)
        print("connection failed")

if __name__ == "__main__":
    channel = thingspeak.Channel(id=channel_id, api_key=write_key)

    while True:
        measure(channel)
        # free account has an api limit of 15sec
        time.sleep(15)
