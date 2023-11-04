This is an example of how input/output could look like.

# Input
- config.ini: our search parameters
- crontab: We have this installed on a uberspace (webserver, hosting our website and a python3 environment). It makes backup copies of the script's output and saves it into a backup folder on a daily / monthly basis before running the script. You can see that we have "search" set to "False", since we know there are no new videos from us posted at the moment. This is in order to save on googleAPI queries.
- yt_ids.csv: File with all youtube IDs to be updated. The ids result from our previous search using the script. You can manually add entries in new lines.

# Output
- week17.csv: This is the outputfile resulting from running the script daily and creating a file every week. You can see all parameters queried by the googleAPI on a daily basis for _all_ our videos.  
- -statisstics.csv: This is the statsfile resulting from running the script daily and creating a new file every month. You find statistics on all videos of TEDxTUM (total views, likes, and so on) on a daily basis.
- log.log: Console log of what happend the last time the script was executed. In this case "search" was enabled and new videos were compared to old ones (as well as double checked whether the return from youtube search really conatins "TEDxTUM"). You can see that quite a lot of videos from search have to be rejected. It is therefor advisable to choose a quite high number of search_results.
- TEDxTUM_views_.png: Possible output when using R to visualize the output from running the script several months.

