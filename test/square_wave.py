from unittest.mock import seal
import matplotlib.pyplot as plt
import seaborn as sns
import time
from datetime import datetime
import json
import pandas as pd

class Square():
    def __init__(self):

        self.step = 0.005
        self.n_period = 7
        self.amplitude = 0.07
        self.sample_freq = 350


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
        # print(f"Data: {self.json_data}")
        
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

    def load_data(self, filename):
        
        # Read lines in JSON format
        df = pd.read_json(filename, orient='records', lines=True)
        # Separate sensors column for each key in dictionary
        df = pd.concat([df.drop(['sensors'],axis = 1),pd.json_normalize(df['sensors'])],axis = 1)
        # Define datetime
        df['DateTime'] = pd.to_datetime(df['timestamp'],format= "%Y-%m-%d %H:%M:%S:%f")
        # Datetime as index
        df = df.set_index('DateTime').drop(["timestamp",],axis = 1)

        self.signal_df = df
        print(df)

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

    def process_data(self,value):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]

        self.save_json([ts,value,0.1])
        self.save_data("square.csv")

        time_to_wait = 1/self.sample_freq
        time.sleep(time_to_wait)


    def square_wave(self):

        counter = 0
        n_loop = 0
        step = 0
        duty_cycle = 0.5
        total_counter = (1/85)*(2/self.step)

        up = True
        down = False
        max_loop = self.n_period
        max_value = self.amplitude
        min_value = 0

        # value = round(initial_value,2)
        # self.process_data(value)
        self.clear_data("square.csv")
        while True:
            if n_loop == max_loop:
                break

            if up:
                self.process_data(max_value+step)
                counter += 1
                if counter == total_counter*duty_cycle:
                    up = False
                    down = True
                    counter = 0

            elif down:
                self.process_data(min_value+step)
                counter += 1
                if counter == total_counter*(1-duty_cycle):
                    up = True
                    down = False
                    counter = 0
                    step += self.step
                    n_loop += 1
                    print(f"Loop number {n_loop}...")

if __name__ == "__main__":

    bla = Square()

    bla.square_wave()
    bla.load_data("square.csv")
    bla.plot_data()
