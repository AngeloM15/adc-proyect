import numpy as np
import logging
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
        log.info(f"Send: {json_data}")
        return json_data

    def save_data(self,filename, jsondata):
        """
        Append data in the last line of the file
        """
        file = open(filename, "a")
        file.write("{}\n".format(jsondata))
        file.close()

    def get_data(self):
        """
        Main function
        """
        # Get times
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Values
        log.info("Sending data through DAC")
        value1 = np.random.randint(0,20)
        log.info("Obtaining data from ADC")
        value2 = np.random.randint(0,10)

        # Save data
        jsondata = self.save_json([ts,value1,value2])

        return jsondata
