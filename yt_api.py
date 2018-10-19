from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


gapi_file = open("gapi.txt","r")

DEVELOPER_KEY = gapi_file.read()
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def youtube_search(searchTerm, maxResults, joiner=','):
    """
    Returns the IDs of videos (as csv) that fit a certain search term 
    :param searchTerm: 
    :param maxResults: 
    :param joiner: 
    :return: 
    """"
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified query term.


  search_response = youtube.search().list(
    q=searchTerm,
    maxResults=maxResults,
    part='id,snippet',
    type='video',
  ).execute()

  token = search_response.get('nextPageToken', None)



  videos = []


  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get('items', []):
    videos.append(search_result['id']['videoId'])



  return joiner.join(videos)

def get_youtube_data(ids):
    """
    Get youtube data from a list of videos
    :param ids: Youtube IDs of all videos to be analysed, comma seperated
    :return:    Pandas Dataframe with video IDs and all metrics & information from snippet and statistics
    """
    response = client.videos().list(
        part='id,snippet, statistics',
        id=ids,

    ).execute()


if __name__ == '__main__':
    print(youtube_search("TEDxTUM", 50, joiner="\n"))

