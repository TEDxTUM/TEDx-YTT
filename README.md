# THIS README IS WIP

# TEDx-YTT
A youtube tracker (YTT) for TEDx videos that tracks the performance of all videos filmed at a specific TEDx
over time using the YoutTube API v2. Each run saves the current likes, views, comments of all videos so historical data
can be tracked and analyzed.

A version of this script has been collecting data for TEDxTUM for ~5 years now. 
A webdashboard showing historical video views, likes and comments can be accessed here.



This README consists of the following parts:
- [General Information](#general-information)
- [Contributing](#contributing)
- [Authors](#authors)
- [License](#license)
- [Acknowledgments](#acknowledgments)
  
## General Information
The script searches the YouTube channel [TEDxTalks](https://www.youtube.com/user/TEDxTalks/) for a specific
 `SEARCH_TERM` (e.g. the TEDx name) and returns all videos with `SEARCH_TERM` in their title as well as their:
- Title
- Youtube ID
- View Count
- Like Count
- Dislike Count (disc. in 2022)
- Comment Count
- Tags
- Thumbnail Image Link
- Publish Day

Data is then augmented with a time stamp and safed to the output file `[BASE_FILENAME]-output.csv` and statistics 
on all numerical data is output to `[BASE_FILENAME]-statistics.csv`. 

There are two versions of the script extracting the data
1. local - that is intended to run locally on your machine or server
2. Google Cloud - that is intended to be used in the Google Cloud

As of today (2023), the Google Cloud (GCP) version is the recommended and maintained version.
The local version (including data visualization scripts and a web dashboard) is provided in the `local` directory
in this repository.
The Google Cloud version is provided in the `Google Cloud` directory and includes the necessary 
requirements.txt and main.py to be run as a Cloud Function on GCP

## Google Cloud Project Setup
### General Setup
The script that scrapes the data from the YouTube API is intended to be run as Google Cloud Function.
All necessary information for the script is stored in the environment variables of the Cloud Function
(including the YouTube API Key).

The script is triggered by a Cloud Scheduler Job that uses a Pub/Sub action to publish either
"update" or "search" as a payload, determining whether new videos should be searched or only data 
from the alreay known videos should be updated.

The data is then saved as `csv` file on `Cloud Storage` as well as written to a table in a dataset on `BigQuery`. 
The Bigquery dataset is then connected to LookerStudio to create accessible (BI) dashboard 
that is accessible through http (and that can be embedded on your webpage).

### Steps to get TEDxYTT running on GCP
The following outlines the steps to be taken to manually set up TEDxYTT. Plans for the future include IaaS and CloudBuild code so this can be done in a few simple steps.
Until then: 
1. Set up a GCP Project including an associated payment account. The project will result in costs that have to be tracked regularily. (From experience, they are <1 USD per month)
2. Activate the **YouTube API v2** for this project
3. Copy the API key and safe it as secret in the **SecretManager**. Save the name of the secret where you can find it (will be needed for environment variables) this is to make sure you don't accidentally share your API with the public.
4. Set up a **PUB/SUB** topic
5. Set up a bucket (i.e. folder) in google **Cloud Storage** and save the name somewhere you can find it (will be needed for environment variables later). This is where the csv files will go and where the youtube IDs will be saved.
6. Set up a **BigQuery** dataset including the two tables 'data-all' and 'stats-all'. They can be empty. Make sure to pick the same region as for google cloud storage (and later cloud function)
7. Add `main.py` and `requirements.txt` to a zip and use this to set up a **CloudFunction**. Use the previously created PubSub as **Eventarc**-Trigger. Depending on the amount of videos you already published, you may need to set the RAM higher than the minimum (512 MiB should work for most, many will make due with 256 MiB). You also have to set the following environment variables:

| Name            | Value                                       | Description |
|-----------------|---------------------------------------------| ----------- |
| GCP_BUCKET_NAME | Name of the bucket created in step 5        | csv files and YouTube Ids will be saved here.
| SEARCH_TERM     | Your TEDx's name, e.g. TEDxTUM              | Tells the script which term to search for. Will automatically also search for combinations of SEARCHTERM and Women, Salon and Youth.
| SEARCH          | True or False                               | Determines whether new videos will be searched or not. Is overwritten by the payload of your pubsub message (see below)
| MAX_RESULTS     | a number 1-1000                             | Maximum results analyzed from youtube search with `SEARCH_TERM`. Every API call returns 50 results, i.e. multiples of 50 make sense. You may run into quota issues with too high numbers (400 works just fine)
| UPDATE          | True or False                               | Defines whether `[BASE_FILENAME]-output` and `[BASE_FILENAME]-stastics` are updated with new data from youtube. Set to `False` if you only want to run statistics on an old file without updating it with new data.
| BASE_FILENAME   | string                                      | Defines how `[BASE_FILENAME]-output` and `[BASE_FILENAME]-stastics` are named.
| NEWOUTPUT_WEEKDAY | a day between monday-sunday                 | Day of the week at which the current output file is renamed into `[BASE_FILENAME]-output_week[calendarweek]`
| NEWSTATS_DAY    | a number between 1-27                       | Day of the month at which the current statistics file is renamed into  `[BASE_FILENAME]-stastics_[current month]`
| GCP_SECRET | ID of the the secret generated in 3.        | Location of the YouTube API Key, that the scrip should use
| ALLTABLE| name of the `all-data` table generated in 6 | Script writes data to this SQL database
|STATSTABLE| name of the `all-data` table generated in 6 | Script writes calculated statistics to this SQL database

Set the entry point for the Cloud Function to `trigger_pubsub`
8. Set up your **CloudScheduler** to post either 'update' or 'search' to the pubsub topic defined in step 4. Cloud Scheduler follows Cron Syntax:
```
# * * * * * 
# ┬ ┬ ┬ ┬ ┬
# │ │ │ │ │
# │ │ │ │ │
# │ │ │ │ └───── day of week (0 - 7) (0 to 6 are Sunday to Saturday, or use names; 7 is Sunday, the same as 0)
# │ │ │ └────────── month (1 - 12)
# │ │ └─────────────── day of month (1 - 31)
# │ └──────────────────── hour (0 - 23)
# └───────────────────────── min (0 - 59
```
E.g. to post the message each day of the week at 7 am, you would add a Job with time '0 7 * * *'. For each monday at 9:05 am you would use '5 9 * * 1'
9. Wait for the first execution of the function or go to **Cloud Scheduler**, select the job that includes search and click "Force Execution". Check in BigQuery whether the tables are filled (you can check the "schema" if its not empty, theres data)
10. Use LookerStudio to set up a Dashboard.




# Contributing
If you want to contribute to the improvement of TEDx-YTT, please have a look [here](../CONTRIBUTING.md)


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
