# THIS README IS WIP

# TEDx-YTT
A youtube tracker (YTT) for TEDx videos that tracks data of a specific TEDx using the google API. Through repeated usage, 
historical data can be tracked and analyzed.

This README consists of the following parts:
- [General Information](#general-information)
- [Contributing](#contributing)
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
- Dislike Count (disc. in 2022)
- Comment Count
- Tags
- Thumbnail Image Link
- Publish Day

Data is then added with a time stamp in each row to the output file `[BASE_FILENAME]-output.csv` and statistics 
on all numerical data is output to `[BASE_FILENAME]-statistics.csv`. 

There are two versions of this YouTube Scraper
1. local - that is intended to run locally on your machine or server
2. Google Cloud - that is intended to be used in the Google Cloud

As of today (2023), the google cloud version is the recommended and maintained version, the local version 
(including data visualization scripts and a webdashboard) is provided in the `local` directory in this repository.

# General Setup
Cloud Function as serverless deployment
Pub/Sub as Trigger
Cloud Scheduler publishes message to topic that Cloud Function is subscribed to
YT API Key & Secret Manager
Cloud Storage to store CSV as backup
BigQuery to save data and make it accessible via Looker Studio
Looker Studio as Dashboard

The behaviour is ... by environment variables.
Future: Infrastructure as Code + Cloud Deploy for easy setup for other TEDx groups 

To make sure little to no data is lost if files get corrupted due to unforseen interrupts of the script (e.g. caused by server reboot if run on a server) data is saved according to the following scheme:
- Current data always has the filename `[BASE_FILENAME]-output.csv` / `[BASE_FILENAME]-statistics.csv`
- Every week, the -output-File is renamed into `[BASE_FILENAME]-output_[year]_week[calendar_week].csv` and therefore effectifely 'stored' in a separate file.
- Every month, the -statistics-File is renamed into `[BASE_FILENAME]-statistics_[year]_[month].csv` (where `[month]` is an integer) and therefore effectifely 'stored' in a separate file.



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
