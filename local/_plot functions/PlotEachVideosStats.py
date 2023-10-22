import pandas as pd
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import os


# path to output csv files
path = r'../output'


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

names = data["Speaker Name"].unique()

all_speakers = []

for name in names:
    print(name)
    print(data.loc[data["Speaker Name"] == name])
    #speaker = data[data["Speaker Name"].str.contains(name)]
    speaker = data.loc[data["Speaker Name"] == name]
    all_speakers.append(speaker)
    fig, axes = plt.subplots(2, 2, sharex='all', figsize=(20, 10))

    axes[0, 0].set_title("Views")
    axes[0, 1].set_title("Likes")
    axes[1, 0].set_title("Percentage Change (Views)")
    axes[1, 1].set_title("Comment Count")

    speaker_change = speaker["Views"].pct_change()
    speaker.plot(use_index=True, y="Views", ax=axes[0, 0])
    speaker.plot(use_index=True, y="Likes", ax=axes[0, 1])
    speaker_change.plot(use_index=True, y="Views", ax=axes[1, 0])
    speaker.plot(use_index=True, y="Comment Count", ax=axes[1, 1])

    axes[0, 1].set_ylim(bottom=0)
    axes[1, 1].set_ylim(bottom=0)

    for ax in axes.flat:
        ax.tick_params(axis='x', labelrotation=90)
        ax.xaxis.grid(True, which="major")
        ax.yaxis.grid()
        ax.xaxis.set_major_locator(dates.MonthLocator())
        ax.xaxis.set_major_formatter(dates.DateFormatter('%b-%y'))
        try:
            ax.get_legend().remove()
        except AttributeError:
            print("No legend to remove")

    plt.suptitle(f'{name} - YouTube Statistics')
    if not os.path.exists('../graphs'):
        os.makedirs('../graphs')
    plt.savefig(f'graphs/{name}_stats.png')
    plt.close()
