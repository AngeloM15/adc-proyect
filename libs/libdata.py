import numpy as np
import pandas as pd
import logging
import time
import json
from datetime import datetime

import seaborn as sns
import matplotlib.pyplot as plt

import board
import busio
# DAC libraries
import adafruit_mcp4725
# ADC libraries
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn


module_logger = logging.getLogger('main.libdata')
log = logging.getLogger('main.libdata.Libdata')

class Libdata():
    def __init__(self):
        self.total_file_name = None
        self.temporal_file_name = None
        

    def save_json(self,data):
        """
        Set data in JSON format
        """
        json_data ={
            "device": "RodStat-bb663b",
            "timestamp": data[0],
            "sensors":{
                "DAC": data[1],
                "ADC": data[2]
            }
        }
        self.json_data = json_data
        log.debug(f"Data: {self.json_data}")
        


    def save_data(self,filename):
        """
        Append data in the last line of the file
        """
        file = open(filename, "a")
        # file.write("{}\n".format(self.json_data))
        json.dump(self.json_data,file)
        file.write("\n")
        file.close()

    def clear_data(self, filename):
        open(filename, 'w').close()

    def read_data(self, filename):
        
        # Read lines in JSON format
        df = pd.read_json(filename, orient='records', lines=True)
        # Separate sensors column for each key in dictionary
        df = pd.concat([df.drop(['sensors'],axis = 1),pd.json_normalize(df['sensors'])],axis = 1)
        # Define datetime
        df['DateTime'] = pd.to_datetime(df['timestamp'],format= "%Y-%m-%d %H:%M:%S:%f")
        # Datetime as index
        df = df.set_index('DateTime').drop(["timestamp",],axis = 1)

        self.signal_df = df

    def plot_data(self):

        df = self.signal_df
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

class Libconversor(Libdata):
    def __init__(self):
        Libdata.__init__(self)

        # Initialize I2C bus.
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
    def set_dac(self,dac_param):

        # # Initialize MCP4725.
        # self.dac = adafruit_mcp4725.MCP4725(self.i2c)
        # # amp = adafruit_max9744.MAX9744(self.i2c, address=0x60)

        self.scan_rate = dac_param["SCAN_RATE"]
        self.step = dac_param["STEP"]
        
        self.n_period = dac_param["NUMBER_OF_LOOPS"]
        self.initial_value = dac_param["CURVE_PARAMETER"]["initial_value"]
        self.max_value = dac_param["CURVE_PARAMETER"]["max_value"]
        self.min_value = dac_param["CURVE_PARAMETER"]["min_value"]

    def set_adc(self):
        # Create the ADC object using the I2C bus
        self.ads = ADS.ADS1115(self.i2c)
        # Create single-ended input on channel 0
        self.chan0 = AnalogIn(self.ads, ADS.P0)
        # ADC Configuration
        self.ads.mode = Mode.CONTINUOUS
        # self.ads.data_rate = 16

    def send_dac(self, data):

        data_rescaled = (5/3)*(1.5-data)
        # self.dac.normalized_value = data_rescaled/5.18
        # log.info(f"Send to DAC ---> {data}V / {data_rescaled}V / {data_rescaled/5.18}")

    def get_adc(self):
        vol_in = self.chan0.voltage
        amp_in = (vol_in-1.71)*1000/(8.2*1000)
        log.debug(f"voltage: {round(vol_in,2)}V / current: {round(amp_in,2)}A")
        return round(amp_in,2)
        # return np.random.normal()

    def process_data(self,dac_value):

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]

        # Send and receive signal
        self.send_dac(dac_value)
        adc_value = self.get_adc()

        self.save_json([ts,dac_value,adc_value])
        self.save_data(self.total_file_name)
        self.save_data(self.temporal_file_name)

        time_to_wait = self.step/self.scan_rate
        time.sleep(time_to_wait)

    def generate_signal(self):
        """
        Triangular curve generation using JSON parameters
        """
        initial_value = self.initial_value
        step = self.step
        count = 1
        n_loop = 0
        up = True
        down = False
        max_loop = self.n_period
        max_value = self.max_value
        min_value = self.min_value

        value = round(initial_value,2)
        self.process_data(value)

        while True:
            if n_loop == max_loop:
                break

            if (count == 3) and (value ==initial_value):
                count = 1
                n_loop += 1
                log.info(f"Loop number {n_loop}...")
                # print(f"loop number {n_loop}")
            elif up:
                value = round(value + step,2)
                if value <= max_value:
                    self.process_data(value)
                else:
                    value -= step
                    up = False
                    down = True
                    count += 1
                    # print(count)

            elif down:
                value = round(value - step,2)
                if min_value <= value:
                    self.process_data(value)
                else:
                    value += step
                    up = True
                    down = False
                    count += 1
                    # print(count)
