# TEDx-YTT
A youtube tracker (YTT) for TEDx videos that tracks data of a specific TEDx using the google API.

This README consists of the following parts:
- [General Information](#general-information)
- [Contributing](#contributing)
- [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installing packages](#installing-packages)
  * [Installing the Youtube API key](#installing-the-youtube-api-key)
  * [Usage](#usage)
  * [Example](#example)
- [Advanced Usage](#advanced-usage)
  * [Adding videos manually](#adding-videos-manually)
  * [Running the script automatically](#running-the-script-automatically)
  * [Using CRON](#using-cron)
  - [Analyzing Data](#analyzing-data)
  * [Using Python](#using-python)
  * [Using R-Script](#using-r-script)
- [Authors](#authors)
- [License](#license)
- [Acknowledgments](#acknowledgments)
  
## General Information
The script searches the youtube channel ["TEDxTalks"](https://www.youtube.com/user/TEDxTalks/) for a specific
 `SEARCH_TERM` (e.g. the TEDx name) and returns all videos with `SEARCH_TERM` in their title as well as their:
- Title
- Youtube ID
- View Count
- Like Count
- Dislike Count
- Comment Count
- Tags
- Thumbnail Image Link
- Publish Day

Data is then added with a time stamp in each row to the output file `[BASE_FILENAME]-output.csv` and statistics 
on all numerical data is output to `[BASE_FILENAME]-statistics.csv`. 

To make sure little to no data is lost if files get corrupted due to unforseen interrupts of the script (e.g. caused by server reboot if run on a server) data is saved according to the following scheme:
- Current data always has the filename `[BASE_FILENAME]-output.csv` / `[BASE_FILENAME]-statistics.csv`
- Every week, the -output-File is renamed into `[BASE_FILENAME]-output_[year]_week[calendar_week].csv` and therefore effectifely 'stored' in a separate file.
- Every month, the -statistics-File is renamed into `[BASE_FILENAME]-statistics_[year]_[month].csv` (where `[month]` is an integer) and therefore effectifely 'stored' in a separate file.



# Contributing
If you want to contribute to the improvement of TEDx-YTT, please have a look [here](CONTRIBUTING.md)


# Getting Started

These instructions will get you a copy of the project up and running and teach you some basics of how to adjust
 it to your needs. 

## Prerequisites

To get things running you will need

- A download of this repository or your own fork of this project 
(have a look [here](https://help.github.com/articles/fork-a-repo/) on a short how-to)
- Anaconda distribution of Python 3.7+. (get it from [here](https://www.anaconda.com/download/) 
or follow [these](https://www.digitalocean.com/community/tutorials/how-to-install-anaconda-on-ubuntu-18-04-quickstart) instructions on Linux/Ubuntu). If you are working on a machine with windows, make sure python is added to the `Environment Variables` (If you haven't selected this option during installation [here](https://docs.python.org/3/using/windows.html#configuring-python) is how to  do it afterwards)
- A Youtube API Public Data key ([here ](https://www.slickremix.com/docs/get-api-key-for-youtube/)
 is how to get one - Use step 1-8)
- The following python packages: 
    - googleapiclient
    - pandas
    - datetime
    - logging
    - sys    
    - argparse
    - configparser
    - os

## Installing packages   
Depending on your operating system and the python distribution you chose some of these may already be installed.
To test, whether a package has already been installed, you can run the following in the command line:
```
python -c "import NAME_OF_PACKAGE"
```
If there is an error ('ImportError: No module named  NAME_OF_PACKAGE'), the package is not installed and you need 
to manually install it.
To install missing required packages you can use the python package management program 
[pip](https://en.wikipedia.org/wiki/Pip_(package_manager)). 
You can use it directly from your command line to upgrade/install the necessary modules 
 (you might need to run sudo first to get elevated rights):
 ```
 pip install --upgrade NAME_OF_PACKAGE
 ```
IMPORTANT The package `googleapiclient` has to be tested using `googleapiclient` 
and installed with `google-api-python-client`. This means:
```
python -c "import googleapiclient"
```
tests, whether the package is installed and:
 ```
 pip install --upgrade google-api-python-client 
 ```
 installs it if it is not.
 
 ## Installing the Youtube API key
The script calls the youtube API. In order to be able to do that you need a personal API key.
CAREFUL: Too many API calls can result in costs! Deploying the script is at your own risk. 
Check your API calls from time to time on the [API dashboard](http://console.cloud.google.com).
 
In the same folder where 'TEDx-ytt.py' is located, add an empty file named 'yapi.txt' to your 
**local** copy (make sure it is **not** added to your git and synchronized with any public repository!). 
Paste your Youtube API Public Data key 
([here is how to get one](https://www.slickremix.com/docs/get-api-key-for-youtube/)) into the file and save it.
Also delete the example files `tedx-ytt-output.csv` and  `tedx-ytt-statistics.csv` from this folder if they are in there. 
  

## Usage
The script has several parameters that influence its behaviour. The following section describes them and
 how to set them in different ways.

| Parameters | Type | Description |
| ---------- | ---- | ----------- |
| `SEARCH_TERM`              | string | The search term that is matched in youtube search and video title.
| `SEARCH`                   | bool   | Turns searching for new videos on and off. To save API points set this `False` if you know there are not any new videos.
| `MAX_RESULTS`              | integer   | Maximum results analyzed from youtube search with `SEARCH_TERM`. Every API call returns 50 results, i.e. multiples of 50 make sense.
| `UPDATE`                   | bool   | Defines whether `[BASE_FILENAME]-output` and `[BASE_FILENAME]-stastics` are updated with new data from youtube. Set to `False` if you only want to run statistics on an old file without updating it with new data.
| `BASE_FILENAME`            | string | Defines how `[BASE_FILENAME]-output` and `[BASE_FILENAME]-stastics` are named.
| `DIRECTORY`      | string   | Directory (relative to root) where `[BASE_FILENAME]-output` and `[BASE_FILENAME]-stastics` are saved. Denote sub-directories by ´/´ (Forward slash). Use keyword `current` to set it the same directory the script is running in.
| `CONSOLE_LOG` (advanced)   | bool   | Turns logging in console on and off. If you are not sure what this does, keep it `False`.
| `LOG_RETURN` (advanced)     | bool   | Turns logging of results of function calls in console on and off. If you are not sure what this does, keep it `False`.
| `NEWOUTPUT_WEEKDAY` (advanced) | string | Day of the week at which the current output file is renamed into `[BASE_FILENAME]-output_week[calendarweek]`.
| `NEWSTATS_DAY` (advanced)| integer | Day of the month at which the current statistics file is renamed into  `[BASE_FILENAME]-stastics_[current month]`, where [current month] is an integer (e.g. 1 for January).

The advanced parameters are for debugging purposes and should be `False` in normal usage.

All parameters can be set manually in the `config.ini` file in the same folder as `tedx-ytt.py` or passed 
as options when running the script from command line.

**CAREFUL**: Always make sure, all parameters are well defined within the `config.ini` file!
Undefined parameters are currently **not** caught and cause the script to crash.

In command line, an argument (representing a parameter) and its value are passed to the script 
through the following syntax:

 ```cmd
python tedx-ytt.py ARGUMENT VALUE ARGUMENT2 VALUE2
 ```
The following table sums up how the parameters of the script can be set and which data types are expected

| short argument | long argument   | parameter       | type   |
|----------------|-----------------|--------------- |--------|
| -h             | --help          |                |        |
| -q             | --search_term   | `SEARCH_TERM`  | string |
| -s             | --search        | `SEARCH`       | bool   |
| -m             | --max_results   | `MAX_RESULTS`  | integer|
| -u             | --update        | `UPDATE`       | bool   |
| -f             | --base_filename | `BASE_FILENAME`| string |
| -l             | --console_log   | `CONSOLE_LOG`  | bool   |
| -r             | --log_return    | `LOG_RETURN`   | bool   |
| -d             | --directory     | `DIRECTORY`    | string |
|-no             | --newoutput_weekday | `NEW_OUTPUT`   | string |
|-ns             | --newstats_day | `NEWSTATS_DAY` | integer |

All arguments are optional. Calling: 
```cmd
tedx-ytt.py -h
 ```
 will show how the parameters are currently set.


## Example

To start a new search with `200` results for `TEDxMoon` and save the results to files 
starting with `moon-landing` run

```cmd
python tedx-ytt.py -q TEDxMoon -s True -u True -m 200 -f moon-landing
```

or change the `config.ini` to:

```buildoutcfg
[Standard]
search_term = TEDxMoon
search = True
max_results = 200
update = True
base_filename = moon-landing

[Advanced]
console_log = False
log_returns = False
directory = current
newstats_day = 10
newoutput_weekday = monday
```

# Advanced Usage

## Adding videos manually
Due to how youtube ranks search results, sometimes some of your videos may be far down the list and not be 
caught by the script using a reasonable number of `MAX_RESULTS`. If this happens you can manually add videos to be tracked.

The script returns a file called `yt_ids.csv` where all tracked videos are listed by their youtube ID. 
To add a video, simply open it on youtube, get its ID from the address bar of your browser (the number-character 
combination after "?v=" and before the first, optional "#") and paste it as a new row inside `yt_ids.csv`. 
Save the file while tedx-ytt is **not** running and the videos will now be added to the ones to be tracked. 

##  Running the script automatically
 Besides manually running the script you could also automate running it
- on Windows:  e.g. using Windows Task Scheduler ([like this]())
- on Mac:      e.g. using Automator 
(e.g. [like this](http://naelshiab.com/tutorial-how-to-automatically-run-your-scripts-on-your-computer/))
- on any UNIX: e.g. Using CRON ([like this](https://www.raspberrypi.org/documentation/linux/usage/cron.md)) 

The script could run once a day/week automatically on a web-server, 
providing you with daily / weekly statistics on all your videos.
To avoid runaway file-sizes and using up too many resources, 
files generated by the script are renamed every week (output file) or every month (statistics file). 
Remember to join the files before analyzing them. 

## Using CRON
Running the script with options allows it to be run flexibly from a [cronjob](https://de.wikipedia.org/wiki/Cron) 
on a Linux machine. In order to do so, you need to edit your machine's crontab. This is done by:
```
crontab -e
``` 
Within the crontab, in each line, first the time of repetition is defined in the following scheme:
```
# * * * * * command to execute
# ┬ ┬ ┬ ┬ ┬
# │ │ │ │ │
# │ │ │ │ │
# │ │ │ │ └───── day of week (0 - 7) (0 to 6 are Sunday to Saturday, or use names; 7 is Sunday, the same as 0)
# │ │ │ └────────── month (1 - 12)
# │ │ └─────────────── day of month (1 - 31)
# │ └──────────────────── hour (0 - 23)
# └───────────────────────── min (0 - 59
```
All parameters can either be set to a value or "for all" (by using "*" as placeholder)
Following the `TEDxMOON` example from above, editing the crontab in the following way would search for 
new videos every first day of a month at 6.02 a.m 
and update the data on all known videos every day of the week at 7.01 am:
```
2 6 1 * * python tedx-ytt.py -q TEDxMoon -s True -u True 
1 7 * * * python tedx-ytt.py -q TEDxMoon -s False -u True
```
(all other parameters are still defined within `config.ini`).

This will work fine on a local machine with just one python version installed. However, on a remote machine several 
versions of python may be installed. It is therefore of paramount importance to use an absolute path to the python 
installation that is installed and maintained by the user as well as to the script. Furthermore, it might be necessary 
to add the current path variables to the crontab at the beginning of the file.

It is also good practise to keep the 'crontab-scheme' from above within the file:

Putting all together, a crontab may look like this:

```
PATH=my_env_path
1 7 * * * /home/my_python_path/python  /home/my_script_path/tedx-ytt.py -q TEDxMoon -s True -u True 
2 6 1 * * /home/my_python_path/python  /home/my_script_path/tedx-ytt.py -q TEDxMoon -s False -u True

# * * * * * command to execute
# ┬ ┬ ┬ ┬ ┬
# │ │ │ │ │
# │ │ │ │ │
# │ │ │ │ └───── day of week (0 - 7) (0 to 6 are Sunday to Saturday, or use names; 7 is Sunday, the same as 0)
# │ │ │ └────────── month (1 - 12)
# │ │ └─────────────── day of month (1 - 31)
# │ └──────────────────── hour (0 - 23)
# └───────────────────────── min (0 - 59 
```
After typing / copying everything to the file, a simple ":wq" writes and closes the file. 

# Analyzing data

## Using Python
If you want to *slice* the results (i.e. view only certain row-column combinations) this could be done 
quickly in python using pandas.

First you have to import pandas and read in the file
```python
import pandas as pd

df = pd.read_csv(yourFilename, sep=';', encoding='utf-8')
```

Then you need to set the indices. For `[BASE_FILENAME]-output.csv` this is `Date` and `ID` 
and for `[BASE_FILENAME]-output.csv` 
you choose `Date` and `Metric`. For the statistics file:
```python
df.set_index(['Date', 'Metric'], inplace=True)
```
You can then slice the dataframe by addressing the column by its name through `df.name`. 
If, for instance, you want to slice the `Views` 
column, this would be:
```python
views = df.Views
```

To slice for a value within an index column use `df.xs(key=KEY, level=LEVEL, drop_level=True)`. 
This returns all rows that have the value `KEY` in index column `LEVEL` and 
removes the index column (`drop_level=True`)
If you want to keep the index column set `drop_level=False`.
To only list mean values from the above example, use:
```python
views.xs(key='mean', level='Metric', drop_level=True)
```

So all you have to do to return e.g. a time-row of mean values of the statistics and save it as csv is:
```python
import pandas as pd

df = pd.read_csv(YOURFILE, sep=';', encoding='utf-8')
df.set_index(['Date', 'Metric'], inplace=True)
df.Views.xs(key='mean', level='Metric', drop_level=True).to_csv(SAVEFILE, sep=';')

```

## Using TEDx-YTT Plot Scripts

In this archive there are two Python scripts to nicely plot results accumulated after running TEDx-YTT for an 
extended period of time (for instance using one of the above mentioned methods):

* `PlotOverallMean.py` - plots mean views, daily view changes in %, comments & likes averaged over all videos
* `PlotEachVideosStats.py` - plots mean views, daily view changes in %, comments & likes of all videos seperately

In order for those scripts to work, you need to store the  `[BASE_FILENAME]-output.csv` files in a folder 'output' 
and the  `[BASE_FILENAME]-statistics.csv` files in a folder named 'stats' within the same folder as 
`PlotEachVideosStats.py` or `PlotOverallMean.py` respectively (or change the path in line 8 of both scripts).
Running the scripts then produces output like this:\
OverallMean
![Overall Stats](plotted-stats.png)
EachVideoStats
![Each Video Stats](SingleVideoStats.png)

# Authors

* **[Julian M. Dlugosch](https://github.com/JuMaD)** - *Initial work* 
* **[Dora Dzvonyar](http://dzvonyar.com/)**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - 
*Code and Documentation Review* 

See also the list of [contributors](https://github.com/JuMaD/TEDx-YTT/graphs/contributors) 
who participated in this project.

# License

This project is licensed under the MIT License - 
see the [LICENSE.md](https://github.com/JuMaD/TEDx-YTT/blob/master/LICENSE) file for details

# Acknowledgments

* TEDxWilmington for the idea to built a tracker based on the Youtube Data API: [Listen to the Hacking the Red Circle Episode](https://www.stitcher.com/podcast/hacking-the-red-circle/e/56498580)
