import pandas as pd
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as dates


# set relative path to stats csv here
path = r'stats'


all_files = glob.glob(path + "/*.csv")
li = []

for f in all_files:
    df = pd.read_csv(f, sep=";")
    li.append(df)

data = pd.concat(li, axis=0, ignore_index=True)
data["Date"] = pd.to_datetime(data["Date"])

means = data[data["Metric"].str.contains("mean")]
means.sort_values(by="Date")
means.set_index("Date", inplace=True)

print(means.head())

fig, axes = plt.subplots(2, 2, sharex='all', figsize=(20, 10))
means.plot(use_index=True, y="Views", ax=axes[0, 0])
means.plot(use_index=True, y="Likes", ax=axes[0, 1])
views_change = means["Views"].pct_change()

views_change.plot(use_index=True, y="Views", ax=axes[1, 0])
means.plot(use_index=True, y="Comment Count", ax=axes[1, 1])

axes[0, 0].set_title("Views")
axes[0, 1].set_title("Likes")
axes[1, 0].set_title("Daily Percentage  Change (Views)")
axes[1, 1].set_title("Comment Count")
axes[0, 1].set_ylim(bottom=0)
axes[1, 1].set_ylim(bottom=0)
fig.suptitle('Mean Data of all Videos')

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

plt.savefig('_all_stats-mean.png')
# plt.show()
