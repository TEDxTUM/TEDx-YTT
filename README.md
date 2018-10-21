# TEDx-YTT
A youtube tracker (YTT) for TEDx videos that tracks data of a specific TEDx using the google API.

The script searches youtube for a specific `SEARCH_TERM` (e.g. the TEDx name) and returns all videos with `SEARCH_TERM` in their title as well as their:
- Title
- Youtube ID
- View Count
- Like Count
- Dislike Count
- Comment Count
- Tags
- Thumbnail Image Link
- Publish Day

Data is then added with a time stamp in each row to the output file `[BASE_FILENAME]-output.csv` and statistics on all numerical data is output to `[BASE_FILENAME]-statistics.csv`. 


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

To get things running you will need

- A download of this repository or your own fork of this project (have a look [here](https://help.github.com/articles/fork-a-repo/) on a short how-to)
- Anaconda distribution of Python 3.7+ (get it from [here](https://www.anaconda.com/download/) and choose "Add python.exe to search path" during installation)
- The following additional python modules: 

    - google-api-client
    - pandas
    - datetime
    - logging
    - sys
    
 - A Youtube API Public Data key ([here is how to get one](https://www.slickremix.com/docs/get-api-key-for-youtube/)  - Use step 1-8)
    
   

### Installing
First make sure you have :

  - a local copy of this project on your machine
  - installed anaconda 
  - added python to ENVIRONMENT VARIABLES
  
Then, install all required modules. If Python is added to your environment variables (if not: add it [like this](https://goo.gl/GJ9Yza)), run the following code from your command line to upgrade/install the necessary modules  (you might need to run sudo first):
 ```
 pip install --upgrade NAME_OF_MODULE
 ```
 where NAME_OF_MODULE is the name of the module you need to install, e.g.
 ```
 pip install --upgrade google-api-python-client
 ```
 
 Next, in the same folder where 'TEDx-ytt.py' is located, add an empty file named 'yapi.txt' to your **local** copy (make sure it is **not** added to your git and synchronized with any publically available repository!). 
 Paste your Youtube API Public Data key ([here is how to get one](https://www.slickremix.com/docs/get-api-key-for-youtube/)) into the file and save it.
Also delete the example files `tedx-ytt-output.csv` and  `tedx-ytt-statistics.csv` from this folder. 
 
If you want to run the script manually, open `TEDx-ytt.py` in a text editor or IDE and adjust the options that can be found at the top of the script to fit your criteria.
 
 ```python 
##################
# CUSTOMIZE HERE #
##################
SEARCH_TERM = 'TEDxTUM'  # Term to search for - your TEDx's name
SEARCH = False  # Switch searching for new videos on/off
MAX_RESULTS = 200  # number of search results used from search request.
UPDATE = False  # Switch updating statistics on/off
# ADVANCED
BASE_FILENAME = 'TEDx-ytt'  # base filename for output files
CONSOLE_LOG = False  # Switch logging output to python console on/off
#################
# END CUSTOMIZE #
#################
 ```
 
For most cases it will be sufficient to set `SEARCH_TERM` accordingly and keep everything else as is. If there are no new videos, setting `SEARCH` to `False` will save on google quota cost (costs: 100 per search of 50 results).


## Deployment

To add today's youtube data to both the  `[BASE_FILENAME]-output` and `[BASE_FILENAME]-stastics` simply run the script with `UPDATE = True`.

The paramters `SEARCH_TERM, SEARCH, MAX_RESULTS, UPDATE, BASE_FILENAME, CONSOLE_LOG` can be either set directly in the script (See last step in [Installing](Installing)) or be passed as optional arguments to the script when running it from the command line.

An argument and its value are passed to the script through the following syntax:

 ```cmd
tedx-ytt.py ARGUMENT VALUE ARGUMENT2 VALUE2
 ```
The following table sums up how the parameters of the script can be set and which data types are expected

| short argument | long argument   | paramter      | type   |
|----------------|-----------------|---------------|--------|
| -h             | --help          |               |        |
| -q             | --search_term   | SEARCH_TERM   | string |
| -s             | --search        | SEARCH        | bool   |
| -m             | --max_results   | MAX_RESULTS   | int    |
| -u             | --update        | UPDATE        | bool   |
| -f             | --base_filename | BASE_FILENAME | string |
| -l             | --console_log   | CONSOLE_LOG   | bool   |

All arguments are optional. Calling 
```cmd
tedx-ytt.py -h
 ```
 will show how the parameters are currently set within `tedx-ytt.py`.
 
 Besides manually running the script you could also automate running it
- on Windows:  e.g. using Windows Task Scheduler ([like this]())
- on Mac:      e.g. using Automator (e.g. [like this](http://naelshiab.com/tutorial-how-to-automatically-run-your-scripts-on-your-computer/))
- on any UNIX: e.g. Using CRON ([like this](https://www.raspberrypi.org/documentation/linux/usage/cron.md)) 
 
### Example
To start a new search with `200` results for `TEDxMoon` and save the results to files starting with `moon-landing` run

```cmd
tedx-ytt.py -q TEDxMoon -s True -u True -m 200 -f moon-landing
```

## Authors

* **Julian M. Dlugosch** - *Initial work* - [JuMaD](https://github.com/JuMaD)

See also the list of [contributors](https://github.com/JuMaD/TEDx-YTT/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/JuMaD/TEDx-YTT/blob/master/LICENSE) file for details

## Acknowledgments

* TEDxWilmington for the idea to built a tracker based on the Youtube Data API
