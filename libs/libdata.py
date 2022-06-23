import numpy as np
import pandas as pd
import logging
import time
import json
from datetime import datetime

import seaborn as sns
import matplotlib.pyplot as plt

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
            "device": "xxxx",
            "timestamp": data[0],
            "sensors":{
                "DAC": data[1],
                "ADC": data[2]
            }
        }
        self.json_data = json_data
        log.info(f"Data: {self.json_data}")
        


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

    def plot_data(self, filename):
        print(filename)
        df = pd.read_json(filename, orient='records', lines=True)

        # Separate sensors column for each key in dictionary
        df = pd.concat([df.drop(['sensors'],axis = 1),pd.json_normalize(df['sensors'])],axis = 1)
        # Define datetime
        df['DateTime'] = pd.to_datetime(df['timestamp'])
        # Datetime as index
        df = df.set_index('DateTime').drop(["timestamp",],axis = 1)

        print(df)
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

    def set_dac(self,dac_param):

        self.scan_period = dac_param["SCAN_PERIOD"]
        self.n_period = dac_param["NUMBER_OF_LOOPS"]
        self.initial_value = dac_param["CURVE_PARAMETER"]["initial_value"]
        self.max_value = dac_param["CURVE_PARAMETER"]["max_value"]
        self.min_value = dac_param["CURVE_PARAMETER"]["min_value"]
    
    def send_dac(self, data):
        pass

    def get_adc(self):
        return np.random.normal()

    def process_data(self,dac_value):

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Send and receive signal
        self.send_dac(dac_value)
        adc_value = self.get_adc()

        self.save_json([ts,dac_value,adc_value])
        self.save_data(self.total_file_name)
        self.save_data(self.temporal_file_name)

        time.sleep(1)

    def generate_signal(self):

        initial_value = self.initial_value
        step = self.scan_period/1000
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
