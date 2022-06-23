import numpy as np
import logging
import time
from datetime import datetime


module_logger = logging.getLogger('main.libdata')
log = logging.getLogger('main.libdata.Libdata')

class Libdata():
    def __init__(self):
        pass

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
        log.info(f"Data: {json_data}")
        return json_data

    def save_data(self,filename, jsondata):
        """
        Append data in the last line of the file
        """
        file = open(filename, "a")
        file.write("{}\n".format(jsondata))
        file.close()

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
        return np.random.randint(0,10)

    def process_data(self,dac_value):
        
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Send and receive signal
        self.send_dac(dac_value)
        adc_value = self.get_adc()

        json_data = self.save_json([ts,dac_value,adc_value])
        self.save_data(self.file_name,json_data)
        time.sleep(1)

    def generate_signal(self, file_name):
        self.file_name = file_name
        
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
                print(f"loop number {n_loop}")
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
