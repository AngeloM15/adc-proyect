import json


class Data:
    def __init__(self):
        self.total_file_name = None
        self.temporal_file_name = None

    def save_json(self, data):
        """
        Set data in JSON format
        """
        json_data = {
            "device": "RodStat-bb663b",
            "timestamp": data[0],
            "sensors": {"DAC": data[1], "ADC": data[2]},
        }
        self.json_data = json_data
        # log.debug(f"Data: {self.json_data}")

    def save_data(self, filename):
        """
        Append data in the last line of the file
        """
        with open(filename, "a", encoding="utf-8") as f:
            json.dump(self.json_data, f)
            f.write("\n")

        # file = open(filename, "a")
        # # file.write("{}\n".format(self.json_data))
        # json.dump(self.json_data, file)
        # file.write("\n")
        # file.close()

    def clear_data(self, filename):
        open(filename, "w", encoding="utf-8").close()

    def load_data(self, filename):

        # Read lines in JSON format
        df = pd.read_json(filename, orient="records", lines=True)
        # Separate sensors column for each key in dictionary
        df = pd.concat(
            [df.drop(["sensors"], axis=1), pd.json_normalize(df["sensors"])], axis=1
        )
        # Define datetime
        df["DateTime"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S:%f")
        # Datetime as index
        df = df.set_index("DateTime").drop(
            [
                "timestamp",
            ],
            axis=1,
        )

        self.signal_df = df

    def filter_data(self, df, filter_factor):

        # Eliminante points that aren't in states change
        df = df.reset_index()
        df_to_filter = pd.DataFrame(columns=df.columns)

        for i, row in df.iterrows():

            if i > 0:
                if row["DAC"] != df["DAC"].iloc[i - 1]:
                    df_to_filter = pd.concat([row.to_frame().T, df_to_filter])
            elif i == 0:
                df_to_filter = pd.concat([df_to_filter, row.to_frame().T])

        df["DateTime"] = pd.to_datetime(df["DateTime"], format="%Y-%m-%d %H:%M:%S:%f")
        df_to_filter = df_to_filter.set_index("DateTime").sort_index()

        # Get al positive peaks
        df_pos = df_to_filter.loc[df_to_filter["ADC"] > 0]
        log.info(f"positive filter table:\n{df_pos}")

        # Get al negative peaks
        df_neg = df_to_filter.loc[df_to_filter["ADC"] < 0]
        # Add firt positive value
        first_row = df_to_filter.iloc[0, :].to_frame().T
        df_neg = pd.concat([first_row, df_neg])
        log.info(f"negative filter table:\n{df_neg}")

        # Set dataframe to plot ADC vs DAC
        df_inter = df_to_filter.copy()
        df_inter["up_env"] = df_pos["ADC"].astype(float)
        df_inter["down_env"] = df_neg["ADC"].astype(float)

        df_inter.drop(["ADC", "device"], axis=1, inplace=True)
        df_inter.reset_index(drop=True, inplace=True)
        df_inter.sort_values(by=["DAC"], ascending=False, inplace=True)
        # Interpolate
        df_inter.interpolate(inplace=True)
        # Smooth
        df_inter = df_inter.ewm(com=filter_factor).mean()

        df_inter["total"] = df_inter["down_env"] - df_inter["up_env"]
        df_inter = df_inter.melt(id_vars=["DAC"])
        log.info(f"filter table w interpolation:\n{df_inter}")

        return df_inter, df_pos, df_neg

    def plot_data(self, type_wave, filter_factor):

        df = self.signal_df

        # Plot data
        sns.set(style="darkgrid", context="paper", rc={"figure.figsize": (10, 8)})
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

        if type_wave == "triangular":
            sns.lineplot(data=df, x=df.index, y="DAC", ax=ax1)
            sns.lineplot(data=df, x=df.index, y="ADC", ax=ax2)
            plt.tight_layout()
            plt.show()

            # Smooth
            df = df.ewm(com=filter_factor).mean()
            g = sns.lineplot(
                data=df, x="DAC", y="ADC", sort=False, lw=1, estimator=None
            )
            plt.xlabel("Potencial (V)")
            plt.ylabel("Corriente (uA)")
            plt.tight_layout()
            plt.show()

        if type_wave == "square":

            df_interpolate, df_positive, df_negative = self.filter_data(
                df, filter_factor
            )

            sns.lineplot(data=df, x=df.index, y="DAC", ax=ax1)
            sns.lineplot(data=df, x=df.index, y="ADC", ax=ax2)
            sns.lineplot(data=df_positive, x=df_positive.index, y="ADC", ax=ax2)
            sns.lineplot(data=df_negative, x=df_negative.index, y="ADC", ax=ax2)
            plt.tight_layout()
            plt.show()

            sns.lineplot(
                data=df_interpolate,
                x="DAC",
                y="value",
                hue="variable",
                sort=False,
                lw=1,
                estimator=None,
            )
            plt.xlabel("Potencial (V)")
            plt.ylabel("Corriente (uA)")
            plt.tight_layout()
            plt.show()
