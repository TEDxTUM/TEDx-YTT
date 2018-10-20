from googleapiclient.discovery import build
import pandas as pd
import datetime
import logging
import sys
import argparse





##################
# CUSTOMIZE HERE #
##################
SEARCH_TERM = 'TEDxTUM'  # Term to search for - your TEDx's name
SEARCH = False  # Switch searching for new videos on/off
MAX_RESULTS = 200  # number of search results used from search request.
UPDATE = False  # Switch updating statistics on/off
# ADVANCED
BASE_FILENAME = 'TEDx-ytt'
CONSOLE_LOG = False  # Switch logging output to python console on/off
#################
# END CUSTOMIZE #
#################



def youtube_search(search_term, max_results, client):
    """
    Returns the IDs of videos (as csv) that fit a certain search term 
    :param search_term: The term to search for
    :param max_results: Maximum number of search results to consider. Each search returns 50 results per iteration.
    :param client: youtube API client
    :return: Comma seperated list of youtube IDs
    """
    logging.info(f'Searching for youtube videos with search term \'{SEARCH_TERM}\'')

    if max_results > 50:
        search_response = client.search().list(
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
                    logging.debug('Found new video: ' + search_result['snippet']['title'])
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
            if 'TEDXTUM' in search_result['snippet']['title'].upper():
                videos.append(search_result['id']['videoId'])

    logging.info(f'...done!')
    return '\n'.join(videos)


def get_youtube_data(ids_str, client):
    """
    Get youtube data from a list of videos
    :param ids_str: Youtube IDs of all videos to be analysed, comma separated
    :param client: youtube client (from youtube API)
    :return:    Pandas Dataframe with video IDs and all metrics & information from snippet and statistics
    """
    logging.info(f'Getting data from youtube ...')

    ids = []
    titles = []
    thumbnail_urls = []
    tags = []

    views = []
    likes = []
    dislikes = []
    favourites = []
    comments = []

    published = []

    dates = []

    keys = [
        'ID',
        'Title',
        'Thumbnail',
        'Tags',
        'Views',
        'Likes',
        'Dislikes',
        'Favourite Count',
        'Comment Count',
        'Date',
        'Published on'
    ]
    values = [ids,
              titles,
              thumbnail_urls,
              tags,
              views,
              likes,
              dislikes,
              favourites,
              comments,
              dates,
              published
              ]

    for id in ids_str.split(','):
        response = client.videos().list(
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
            favourites.append(result['statistics'].get('favoriteCount', '0'))
            comments.append(result['statistics'].get('commentCount', '0'))

            dates.append(date)

    d = dict(zip(keys, values))
    df = pd.DataFrame(d)
    df.set_index(['Date', 'ID'], inplace=True)

    logging.info(f'...done!')
    return df


def load_data(filename):
    """
    Loads a csv into a dataframe with multi-index ['Date', 'ID']
    :param filename: Name of the csv file
    :return: pandas dataframe containing the data with  multi-index ['Date', 'ID']
    """
    logging.info(f'Loading old data from {filename}')
    try:
        df = pd.read_csv(filename, sep=';', encoding='latin-1')
        df.set_index(['Date', 'ID'], inplace=True)
    except FileNotFoundError:
        logging.warning(f'File {filename} does not exist! Continuing without loading old data.')
        df = None

    logging.info(f'...done!')
    return df

# todo: unify load_data functions


def load_stats_data(filename):
    """
    Loads a csv into a dataframe with multi-index ['Date', 'Metric']
    :param filename: Name of the csv file
    :return: pandas dataframe containing the data with  multi-index ['Date', 'ID']
    """

    logging.info(f'Loading old statistics from {filename}')
    try:
        df = pd.read_csv(filename, sep=';', encoding='latin-1')
        df.set_index(['Date', 'Metric'], inplace=True)
    except FileNotFoundError:
        logging.warning(f'File {filename} does not exist! Continuing without loading old data.')
        df = None

    logging.info(f'...done!')

    return df


def calc_stats(df):
    """
    Calculates statistics (pd.describe()) on all numeric columns
    :param df: pandas df to be described
    :return: pandas df with all statistics and multi-index ['Date', 'Metric']
    """

    logging.info('Calculating statistics ... ')
    df_copy = df.copy()
    df_copy.drop(labels=['Published on', 'Tags', 'Thumbnail', 'Title'], axis=1, inplace=True)

    dates = []
    date = datetime.datetime.now().date()
    described = df_copy.astype('float64').describe(include='all')

    for row in range(0, described.shape[0]):
        dates.append(date)

    described['Date'] = dates
    described.reset_index(inplace=True)

    described.rename(columns={'index': 'Metric'}, inplace=True)

    described.set_index(['Date', 'Metric'], inplace=True)
    logging.info('... done')

    return described


if __name__ == '__main__':
    #Parse args

    parser = argparse.ArgumentParser(description='Search for a TEDx on youtube and '
                                                 'return stats to all videos with that TEDx in title.')
    parser.add_argument('-q', '--search_term', help='Term to search for - your TEDx\'s name', type=str)
    parser.add_argument('-s', '--search', help='Switch searching for new videos on/off', type=bool)
    parser.add_argument('-m', '--max_results', help='Number of search results used from search request.', type=int)
    parser.add_argument('-u', '--update', help='Switch updating statistics on/off', type=bool)
    parser.add_argument('-f', '--base_filename', help='Term to search for - your TEDx\'s name', type=str)
    parser.add_argument('-l', '--console_log', help='Switch logging output to python console on/off', type=bool)
    args = parser.parse_args()

    if args.search_term:
        SEARCH_TERM = args.search_term
    if args.search:
        SEARCH = args.search
    if args.max_results:
        MAX_RESULTS = args.max_results
    if args.update:
        SUPDATE = args.update
    if args.base_filename:
        BASE_FILENAME = args.search_term
    if args.console_log:
        CONSOLE_LOG = args.search_term
    #Logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename='log.log',
                        filemode='w')
    if CONSOLE_LOG:
        root = logging.getLogger()
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
    YAPI_FILE = open('yapi.txt', 'r')

    DEVELOPER_KEY = YAPI_FILE.read()
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    old_df = load_data(f'{BASE_FILENAME}-output.csv')

    if SEARCH:
        yt_ids = youtube_search(SEARCH_TERM, MAX_RESULTS, client=youtube)
    else:
        try:
            yt_ids = ','.join(old_df.index.levels[1])
        except:
            logging.warning('There is no old data available. Please run script again with SEARCH = True.')
            yt_ids = None
            exit(1)

    if UPDATE and yt_ids is not None:
        new_df = get_youtube_data(yt_ids.replace('\n', ','), youtube)
        if old_df is not None:
            final_df = pd.concat([old_df, new_df], axis=0, join='inner')
            final_df.drop_duplicates(inplace=True)

        else:
            final_df = new_df
    else:
        final_df = old_df
        new_df = old_df

    old_stats_df = load_stats_data(f'{BASE_FILENAME}-statistics.csv')

    if old_stats_df is not None and UPDATE:
        new_stats_df = calc_stats(new_df)
        final_stats_df = pd.concat([old_stats_df, new_stats_df], axis=0, join='inner')
        final_stats_df.drop_duplicates(inplace=True)

    elif UPDATE:
        new_stats_df = calc_stats(new_df)
        final_stats_df = new_stats_df

    elif old_stats_df is not None:
        final_stats_df = old_stats_df
    else:
        final_stats_df = calc_stats(new_df)

    logging.info('Saving data ...')

    final_df.to_csv(f'{BASE_FILENAME}-output.csv', sep=';')
    final_stats_df.to_csv(f'{BASE_FILENAME}-statistics.csv', sep=';')

    logging.info(f'...done!')
    print('Done!')
