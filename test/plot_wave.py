import os
import matplotlib.pyplot as plt
import pandas as pd
import json
import seaborn as sns

HOME = os.path.expanduser('~')+"/git_test/potenciostato-project"

def load_data(filename):

    # Read lines in JSON format
    df = pd.read_json(filename, orient='records', lines=True)
    # Separate sensors column for each key in dictionary
    df = pd.concat([df.drop(['sensors'],axis = 1),pd.json_normalize(df['sensors'])],axis = 1)

    # Define datetime
    df['DateTime'] = pd.to_datetime(df['timestamp'],format= "%Y-%m-%d %H:%M:%S:%f")
    # Datetime as index
    df = df.set_index('DateTime').drop(["timestamp",],axis = 1)

    return df

def filter_data(df):

    # Eliminante points that aren't in states change
    df = df.reset_index()
    df_to_filter = pd.DataFrame(columns = df.columns)

    for i, row in df.iterrows():

        if i > 0:
            if row["DAC"] != df["DAC"].iloc[i-1]:
                df_to_filter=pd.concat([row.to_frame().T,df_to_filter])
        elif i == 0:
            df_to_filter=pd.concat([df_to_filter,row.to_frame().T])

    df['DateTime'] = pd.to_datetime(df['DateTime'],format= "%Y-%m-%d %H:%M:%S:%f")
    df_to_filter = df_to_filter.set_index('DateTime').sort_index()
    print(f"filter table:\n{df_to_filter}")

    # Get al positive peaks
    df_pos = df_to_filter.loc[df_to_filter["ADC"]>0]
    print(f"positive filter table:\n{df_pos}")

    # Get al negative peaks
    df_neg = df_to_filter.loc[df_to_filter["ADC"]<0]
    # Add firt positive value
    first_row = df_to_filter.iloc[0,:].to_frame().T
    df_neg = pd.concat([first_row, df_neg])
    print(f"negative filter table:\n{df_neg}")

    # Set dataframe to plot ADC vs DAC
    df_inter = df_to_filter.copy()
    df_inter["up_env"] = df_pos["ADC"].astype(float)
    df_inter["down_env"] = df_neg["ADC"].astype(float)

    df_inter.drop(["ADC","device"],axis = 1,inplace = True)
    df_inter.reset_index(drop =True,inplace = True)
    df_inter.sort_values(by=["DAC"], ascending = False,inplace = True)
    df_inter.interpolate(inplace = True)

    df_inter["total"] = df_inter["down_env"]- df_inter["up_env"]
    df_inter = df_inter.melt(id_vars = ["DAC"])
    print(f"filter table:\n{df_inter}")

    return df_inter,df_pos,df_neg

def plot_data(df,type_wave):

    # Plot data
    sns.set(style="darkgrid", context = "paper", rc={'figure.figsize':(14,8)})
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    if type_wave == "triangular":
        sns.lineplot(data = df, x = df.index, y = "DAC", ax = ax1)
        sns.lineplot(data = df, x = df.index, y = "ADC", ax = ax2)
        plt.tight_layout()
        plt.show()

        g = sns.lineplot(data = df, x="DAC", y="ADC", sort=False, lw=1, estimator=None)
        plt.xlabel("Potencial (V)")
        plt.ylabel("Corriente (uA)")
        plt.tight_layout()
        plt.show()

    if type_wave == "square":

        df_interpolate, df_positive, df_negative = filter_data(df)

        sns.lineplot(data = df, x = df.index, y = "DAC", ax = ax1)
        sns.lineplot(data = df, x = df.index, y = "ADC", ax = ax2)
        sns.lineplot(data = df_positive, x = df_positive.index, y = "ADC", ax = ax2)
        sns.lineplot(data = df_negative, x = df_negative.index, y = "ADC", ax = ax2)
        plt.tight_layout()
        plt.show()

        sns.lineplot(data = df_interpolate, x="DAC", y="value",hue ="variable", sort=False, lw=1, estimator=None)
        plt.xlabel("Potencial (V)")
        plt.ylabel("Corriente (uA)")
        plt.tight_layout()
        plt.show()

def main():
    df = load_data(f"{HOME}/data/electrodo-2022-07-04.csv")
    plot_data(df,"square")

if __name__ == "__main__":
    main()

