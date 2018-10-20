from googleapiclient.discovery import build
import pandas as pd
import datetime

YAPI_FILE = open("yapi.txt", "r")
MAX_RESULTS = 300
SEARCH_TERM = "TEDxTUM"
SEARCH = False


def youtube_search(search_term, max_results, youtube):
    """
    Returns the IDs of videos (as csv) that fit a certain search term 
    :param search_term:
    :param max_results:
    :param youtube:
    :return: 
    """

    if max_results > 50:
        search_response = youtube.search().list(
            q=search_term,
            maxResults=50,
            part='id,snippet',
            type='video',
        ).execute()

        videos = []
        for search_result in search_response.get('items', []):
            if SEARCH_TERM.upper() in search_result['snippet']['title'].upper():
                videos.append(search_result['id']['videoId'])

        token = search_response.get('nextPageToken', None)
        remaining_results = max_results - 50

        while token is not None and remaining_results > 50:
            search_response = youtube.search().list(
                q=search_term,
                maxResults=50,
                part='id,snippet',
                type='video',
                pageToken=token
            ).execute()

            for search_result in search_response.get('items', []):
                if SEARCH_TERM.upper() in search_result['snippet']['title'].upper():
                    videos.append(search_result['id']['videoId'])
                    print("Found new video: " + search_result['snippet']['title'])
            token = search_response.get('nextPageToken', None)
            remaining_results = max_results - 50

    else:
        search_response = youtube.search().list(
            q=search_term,
            maxResults=max_results,
            part='id,snippet',
            type='video',
        ).execute()
        videos = []

        for search_result in search_response.get('items', []):
            if "TEDXTUM" in search_result['snippet']['title'].upper():
                videos.append(search_result['id']['videoId'])

    return '\n'.join(videos)


def get_youtube_data(ids_str, youtube):
    """
    Get youtube data from a list of videos
    :param ids_str: Youtube IDs of all videos to be analysed, comma seperated
    :param youtube: youtube client (from youtube API)
    :return:    Pandas Dataframe with video IDs and all metrics & information from snippet and statistics
    """

    ids = []
    titles = []
    thumbnail_urls = []
    tags = []

    views = []
    likes = []
    dislikes = []
    favs = []
    comments = []

    published = []

    dates = []

    keys = [
        "ID",
        "Title",
        "Thumbnail",
        "Tags",
        "Views",
        "Likes",
        "Dislikes",
        "Favourite Count",
        "Comment Count",
        "Date",
        "Published on"
    ]
    values = [ids,
              titles,
              thumbnail_urls,
              tags,
              views,
              likes,
              dislikes,
              favs,
              comments,
              dates,
              published
              ]

    for id in ids_str.split(','):
        response = youtube.videos().list(
            part='id,'
                 'snippet,'
                 ' statistics',
            id=id,
        ).execute()

        date = datetime.datetime.now().date()

        for result in response.get('items', []):
            titles.append(result['snippet']['title'])
            thumbnail_urls.append(result['snippet']['thumbnails']['medium']['url'])
            tags.append(','.join(result['snippet'].get('tags', 'NONE')))
            ids.append(result['id'])
            published.append(result['snippet']['publishedAt'])

            views.append(result['statistics'].get('viewCount', '0'))
            likes.append(result['statistics'].get('likeCount', '0'))
            dislikes.append(result['statistics'].get('dislikeCount', '0'))
            favs.append(result['statistics'].get('favoriteCount', '0'))
            comments.append(result['statistics'].get('commentCount', '0'))

            dates.append(date)

    d = dict(zip(keys, values))
    df = pd.DataFrame(d)
    df.set_index(['Date', 'ID'], inplace=True)

    return df


def load_data(filename):
    """
    Return data frame from file
    :param filename:
    :return:
    """

    df = pd.read_csv(filename, sep=";", encoding='latin-1')
    df.set_index(['Date', 'ID'], inplace=True)

    return df


if __name__ == '__main__':

    DEVELOPER_KEY = YAPI_FILE.read()
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    old_df = load_data('tedy-ytt-output.csv')

    if SEARCH:
        yt_ids = youtube_search(SEARCH_TERM, MAX_RESULTS, youtube=youtube)
    else:
        yt_ids = ','.join(old_df.index.levels[1])

    new_df = get_youtube_data(yt_ids.replace('\n', ','), youtube)

    try:
        final_df = pd.concat([old_df, new_df], axis=0, join='inner')
        final_df.drop_duplicates(inplace=True)
    except:
        final_df = new_df
    final_df.to_csv("tedy-ytt-output.csv", sep=';')
