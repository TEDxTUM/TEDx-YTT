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
 
 Next, in the same folder where 'TEDx-ytt.py' is located, add an empty file named 'yapi.txt' to your **local** copy (make sure it is **not** added to your git and synchronized with any public repository!). 
 Paste your Youtube API Public Data key ([here is how to get one](https://www.slickremix.com/docs/get-api-key-for-youtube/)) into the file and save it.
Also delete the example files `tedx-ytt-output.csv` and  `tedx-ytt-statistics.csv` from this folder. 
  


## Deployment
The script has the following parameters:

| Parameters | Type | Description |
| ---------- | ---- | ----------- |
| `SEARCH_TERM`              | string | The search term that is matched in youtube search and video title.
| `SEARCH`                   | bool   | Turns searching for new videos on and off. To save API points set this `False` if you know there are not any new videos.
| `MAX_RESULTS`              | int    | Maximum results analyzed from youtube search with `SEARCH_TERM`. Every API call returns 50 results, i.e. multiples of 50 make sense.
| `UPDATE`                   | bool   | Defines whether `[BASE_FILENAME]-output` and `[BASE_FILENAME]-stastics` are updated with new data from youtube.
| `BASE_FILENAME`            | string | Defines how `[BASE_FILENAME]-output` and `[BASE_FILENAME]-stastics` are named.
| `CONSOLE_LOG` (advanced)   | bool   | Turns logging in console on and off.
| `LOG_RETURN` (advanced)     | bool   | Turns logging of results of function calls in console on and off.

The advanced parameters are for debugging purposes and should be `False` in normal usage.
All parameters can be set manually in the `config.ini` file in the same folder as `tedx-ytt.py` or passed as options when running the script from command line.
Always make sure, all parameters are well defined within the `config.ini` file!

In command line, an argument (representing a parameter) and its value are passed to the script through the following syntax:

 ```cmd
tedx-ytt.py ARGUMENT VALUE ARGUMENT2 VALUE2
 ```
The following table sums up how the parameters of the script can be set and which data types are expected

| short argument | long argument   | parameter       | type   |
|----------------|-----------------|--------------- |--------|
| -h             | --help          |                |        |
| -q             | --search_term   | `SEARCH_TERM`  | string |
| -s             | --search        | `SEARCH`       | bool   |
| -m             | --max_results   | `MAX_RESULTS`  | int    |
| -u             | --update        | `UPDATE`       | bool   |
| -f             | --base_filename | `BASE_FILENAME`| string |
| -l             | --console_log   | `CONSOLE_LOG`  | bool   |
| -r             | --log_return    | `LOG_RETURN`   | bool   |

All arguments are optional. Calling: 
```cmd
tedx-ytt.py -h
 ```
 will show how the parameters are currently set.
 
 Besides manually running the script you could also automate running it
- on Windows:  e.g. using Windows Task Scheduler ([like this]())
- on Mac:      e.g. using Automator (e.g. [like this](http://naelshiab.com/tutorial-how-to-automatically-run-your-scripts-on-your-computer/))
- on any UNIX: e.g. Using CRON ([like this](https://www.raspberrypi.org/documentation/linux/usage/cron.md)) 

The script could run once a day/week automatically on an EC2 AWS server, providing you with daily / weekly statistics on all your videos.
 
### Example
To start a new search with `200` results for `TEDxMoon` and save the results to files starting with `moon-landing` run

```cmd
tedx-ytt.py -q TEDxMoon -s True -u True -m 200 -f moon-landing
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
```

## Authors

* **Julian M. Dlugosch** - *Initial work* - [JuMaD](https://github.com/JuMaD)

See also the list of [contributors](https://github.com/JuMaD/TEDx-YTT/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/JuMaD/TEDx-YTT/blob/master/LICENSE) file for details

## Acknowledgments

* TEDxWilmington for the idea to built a tracker based on the Youtube Data API
