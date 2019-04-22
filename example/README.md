This is an example of how input/output could look like.

# Input
- config.ini: our search parameters
- crontab: We have this installed on a uberspace (webserver, hosting our website and a python3 environment). It makes backup copies of the script's output and saves it into a backup folder on a daily / monthly basis before running the script. You can see that we have "search" set to "False", since we know there are no new videos from us posted at the moment. This is in order to save on googleAPI queries.
- yt_ids.csv: File with all youtube IDs to be updated. The ids result from our previous search using the script. You can manually add entries in new lines.

# Output
- week17.csv: This is the outputfile resulting from running the script daily and creating a file every week. You can see all parameters queried by the googleAPI on a daily basis for _all_ our videos.  
- stats.csv: This is the statsfile resulting from running the script daily and creating a new file every month. You find statistics on all videos of TEDxTUM (total views, likes, and so on) on a daily basis.


