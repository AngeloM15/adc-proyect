from itsdangerous import json
import numpy as np
import os
from datetime import datetime

HOME = os.path.expanduser("~")+"/git_test/adc-proyect"

def save_json(data):
    """
    Set data in JSON format
    """
    json_data ={
        "device": "xxxx",
        "timestamp": data[0],
        "sensors":{
            "adc": data[1],
            "dac": data[2]
        }
    }
    return json_data

def save_data(filename, data):
    """
    Append data in the last line of the file
    """
    jsondata = save_json(data)

    file = open(filename, "a")
    file.write("{}\n".format(jsondata))
    file.close()

def get_data():
    """
    Main function
    """
    # Get times
    dt = datetime.now()
    ts = dt.strftime("%Y-%m-%d %H:%M:%S")
    month =dt.strftime("%Y-%m")

    # Values
    value1 = np.random.randint(0,20)
    value2 = np.random.randint(0,10)


    # Save data
    save_data(f"{HOME}/data/raw-data-{month}.csv",[ts,value1,value2])

    return value1, value2
