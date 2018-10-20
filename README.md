# TEDx-YTT --> WIP!!!
A youtube tracker for TEDx videos that tracks data of a specific TEDx using the google API.
The script searches youtube for a specific `SEARCH_TERM` and returns all videos with `SEARCH_TERM` in their title as well as their:
- Title
- Youtube ID
- View Count
- Like Count
- Dislike Count
- Comment Count
- Tags
- Thumbnail Image Link
- Publish Day

Data is then added to the output file 'TEDx-ytt-output.csv' and statistics on all numerical data is output to 'TEDx-ytt-statistics.csv'

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
 
 <>This might be excluded in further versions
 <>todo: automatically make new file on first startup
 
 Add an empty file named 'TEDx-ytt-data.csv' to the folder where 'TEDx-ytt.py' is located.
 
 Open 'TEDx-ytt.py' in a text editor or IDE and adjust the options that can be found at the top of the script to fit your criteria.
 
 ```python 
#CUSTOMIZE HERE
MAX_RESULTS = 300
SEARCH_TERM = "TEDxTUM"
SEARCH = False
#END
 ```
 


End with an example of getting some data out of the system or using it for a little demo




## Deployment

Add additional notes about how to deploy this on a live system

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Julian M. Dlugosch ** - *Initial work* - [JuMaD](https://github.com/JuMaD)

See also the list of [contributors](https://github.com/JuMaD/TEDx-YTT/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* TEDx... for the idea to built a tracker based on Youtube API
