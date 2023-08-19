import pandas as pd
import glob

# Path to output csv files
path = r'output'

all_files = glob.glob(path + "/*.csv")
li = []

for f in all_files:
    df = pd.read_csv(f, sep=";")

    # Remove duplicate rows based on all columns
    df = df.drop_duplicates()

    li.append(df)

data = pd.concat(li, axis=0, ignore_index=True)
data["Date"] = pd.to_datetime(data["Date"])

# Sort the data by 'Date'
data.sort_values(by="Date", inplace=True)

data.set_index("Date", inplace=True)

data.to_csv('all_data.csv', sep=";")