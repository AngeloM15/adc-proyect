import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

HOME = os.path.expanduser('~')+"/potenciostato-project"

def load_data(filename):
    
    # Read lines in JSON format
    df = pd.read_json(filename, orient='records', lines=True)
    # Separate sensors column for each key in dictionary
    df = pd.concat([df.drop(['sensors'],axis = 1),pd.json_normalize(df['sensors'])],axis = 1)
    # Define datetime
    df['DateTime'] = pd.to_datetime(df['timestamp'],format= "%Y-%m-%d %H:%M:%S:%f")
    # Datetime as index
    df = df.set_index('DateTime').drop(["timestamp",],axis = 1)

    return filter_data(df)

def filter_data(df):
    print(df)

def plot_data(self,df):

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

def main():
    
    df = load_data(f"{HOME}/data/tem-data-2022-07.csv")
    filter_data(df)

if __name__ == "__main__":
    main()

