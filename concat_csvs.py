import pandas as pd
import glob
import os


# path to output csv files
path = r'output'

all_files = glob.glob(path + "/*.csv")
li = []

for f in all_files:
    df = pd.read_csv(f, sep=";")
    print(f)
    li.append(df)

data = pd.concat(li, axis=0, ignore_index=True)
data["Date"] = pd.to_datetime(data["Date"])
data.sort_values(by="Date")
data.set_index("Date", inplace=True)


data.to_csv('all_data.csv', sep=";")