#todolist: remove all argparse stuff, move all settings into environment variables, move

from googleapiclient.discovery import build
import pandas as pd
import logging
import sys
import configparser
import datetime
import os
from google.cloud import storage, secretmanager

import base64
import functions_framework
import pathlib


def trace(funct):
    def wrapper(*args, **kwargs):
        if CONSOLE_LOG:
            logging.info(f"TRACE: Calling {funct.__name__}() "
                         f"with {args}, {kwargs}")
        result = funct(*args, **kwargs)
        if LOG_RETURNS:
            logging.info(f'TRACE: {funct.__name__}() '
                         f'returned {result!r}')
        else:
            logging.info(f'TRACE: {funct.__name__}() finished')
        return result

    return wrapper


@trace
def youtube_search(search_term, max_results, client):
    """
    Returns the IDs of videos (as \n separated string) that fit a certain search term
    :param search_term: The term to search for
    :param max_results: Maximum number of search results to consider.
    :param client: youtube API client
    :return: \n separated list of youtube IDs
    """
    search_term = f"{search_term}|{search_term}Salon|{search_term}Youth|{search_term}"
    videos = []
    if max_results > 50:
        search_response = client.search().list(
            q=search_term,
            maxResults=50,
            part='id,snippet',
            type='video',
            channelId='UCsT0YIqwnpJCM-mx7-gSA4Q' #tedx youtube channel
        ).execute()

        videos.extend(
            search_result['id']['videoId']
            for search_result in search_response.get('items', [])
            if SEARCH_TERM.upper() in search_result['snippet']['title'].upper()
        )

        token = search_response.get('nextPageToken', None)
        remaining_results = max_results - 50
        resultsPerPage = search_response.get('pageInfo')['resultsPerPage']


        while token is not None and remaining_results > 50 and resultsPerPage>0:
           search_response = client.search().list(
                q=search_term,
                maxResults=50,
                part='id,snippet',
                type='video',
                channelId='UCsT0YIqwnpJCM-mx7-gSA4Q',
                pageToken=token
            ).execute()
           discard_counter = 0
           for search_result in search_response.get('items', []):
                if SEARCH_TERM.upper() in search_result['snippet']['title'].upper():
                    videos.append(search_result['id']['videoId'])
                    logging.info('Found new video: ' + search_result['snippet']['title'])
                else:
                    logging.info('Discarded video: ' + search_result['snippet']['title'])
                    discard_counter += 1

           logging.debug(f'Discarded video count:{discard_counter}')

           token = search_response.get('nextPageToken', None)
           remaining_results = max_results - 50
           resultsPerPage = search_response.get('pageInfo')['resultsPerPage']
           logging.info(f'ResultsPerPage:{resultsPerPage}')

    else:
        search_response = client.search().list(
            q=search_term,
            maxResults=max_results,
            part='id,snippet',
            type='video',
            channelId='UCsT0YIqwnpJCM-mx7-gSA4Q'
        ).execute()
        videos = [
            search_result['id']['videoId']
            for search_result in search_response.get('items', [])
            if 'TEDXTUM' in search_result['snippet']['title'].upper()
        ]
    return '\n'.join(videos)


@trace
def get_youtube_data(ids_str, client):
    """
    Get youtube data from a list of videos
    :param ids_str: Youtube IDs of all videos to be analysed, comma separated
    :param client: youtube client (from youtube API)
    :return:    Pandas Dataframe with video IDs and all metrics & information from snippet and statistics
    """

    ids = []
    titles = []
    speakers = []
    # tedxs = []

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
        'Speaker Name',
        # 'Tedx Name',
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
              speakers,
              # tedx,
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

    for yt_id in ids_str.split(','):
        response = client.videos().list(
            part='id,'
                 'snippet,'
                 'statistics',
            id=yt_id,
        ).execute()

        if not response.get("pageInfo", [])["totalResults"]:
            logging.warning(f'Incorrect youtube ID: {id}    !')
        date = datetime.datetime.now().date()

        for result in response.get('items', []):

            title = result['snippet']['title']
            if '|' in title:
                from_title = [x.strip() for x in title.split('|')]

                title = from_title[0]
                speaker = from_title[1]
                # tedx = from_title[2]
                logging.info(f'title {title}')
                logging.info(f'speaker {speaker}')

                titles.append(title)
                speakers.append(speaker)
            else:
                titles.append(title)
                speakers.append('n/a')
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

    return df


@trace
def load_data(filename, indices):
    """
    Loads a csv into a dataframe with multi-index ['Date', 'ID']
    :param filename: Name of the csv file
    :param indices: array of indices
    :return: pandas dataframe containing the data with  multi-index ['Date', 'ID']
    """
    logging.info(f'Loading data from {filename}')
    try:
        df = pd.read_csv(filename, sep=';', encoding='utf-8', parse_dates=['Date'])
        df.set_index(indices, inplace=True)
    except FileNotFoundError:
        logging.warning(f'File {filename} does not exist! Continuing without loading old data.')
        df = None

    logging.info('...done!')
    return df


@trace
def load_ids(directory, searched_ids):
    """
    Loads youtube IDs from 'yt_ids.csv' in directory and concats it with searched_ids (result from yt search)
    :param directory: directory where yt_ids is located
    :param searched_ids: result from yt search: \n separated string of yt ids
    :return: \n separated string of yt IDs that are either in the file or in the list from yt search
    """
    logging.info('Loading yt_ids from external file...')
    saved_ids = pd.read_csv(os.path.join(directory, 'yt_ids.csv'),
                            encoding='utf-8').to_string(index=False)

    searched_ids_list = searched_ids.split('\n')
    saved_ids_list = saved_ids.split('\n')

    logging.info(f'IDs in search but not file:\t\t\t{list(set(searched_ids_list) - set(saved_ids_list))}')
    logging.info(f'IDs in yt_ids file but not search:\t{list(set(saved_ids_list) - set(searched_ids_list))}')

    for item in saved_ids_list:
        if item not in searched_ids_list:
            searched_ids_list.append(item)
    logging.info('...done')

    return '\n'.join(searched_ids_list)


@trace
def calc_stats(df):
    """
    Calculates statistics (pd.describe()) on all numeric columns
    :param df: pandas df to be described
    :return: pandas df with all statistics (rounded to integer) and multi-index ['Date', 'Metric']
    """

    df_copy = df.copy()
    df_copy.drop(labels=['Published on', 'Tags', 'Thumbnail', 'Title', 'Speaker Name'], axis=1, inplace=True)

    date = datetime.datetime.now().date()
    described = df_copy.astype('float64').describe(include='all')

    dates = [date for _ in range(described.shape[0])]
    described['Date'] = dates
    described.reset_index(inplace=True)

    described.rename(columns={'index': 'Metric'}, inplace=True)

    described.set_index(['Date', 'Metric'], inplace=True)

    return described.round()


@trace
def rename_cloud_storage_blobs(bucket_name, BASE_FILENAME, NEWOUTPUT_WEEKDAY, NEWSTATS_DAY):
    """
    Function to rename the files on gcp to avoid exponentially increasing file sizes
    :param bucket_name: Name of the bucket in the same project
    :param BASE_FILENAME: from config.ini
    :param NEWOUTPUT_WEEKDAY:
    :param NEWSTATS_DAY:
    :return: None
    """
    today = datetime.datetime.today()
    weekdays = {
        "monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4,
        "friday": 5, "saturday": 6, "sunday": 7
    }

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    if today.isoweekday() == weekdays[NEWOUTPUT_WEEKDAY.lower()]:
        new_output_blob_name = f'output/{BASE_FILENAME}-output_{today.isocalendar()[0]}_week{today.isocalendar()[1]}.csv'
        old_output_blob = bucket.blob(f'output/{BASE_FILENAME}-output.csv')
        new_output_blob = bucket.rename_blob(old_output_blob, new_output_blob_name)

    if today.day == NEWSTATS_DAY:
        new_stats_blob_name = f'stats/{BASE_FILENAME}-statistics_{today.isocalendar()[1]}_{today.month}.csv'
        old_stats_blob = bucket.blob(f'stats/{BASE_FILENAME}-statistics.csv')
        new_stats_blob = bucket.rename_blob(old_stats_blob, new_stats_blob_name)


@trace
def load_data_from_bucket(bucket, blob_name, indices):
    blob = bucket.blob(blob_name)
    data = blob.download_as_text()
    df = pd.read_csv(data, sep=';', encoding='utf-8', parse_dates=['Date'])
    df.set_index(indices, inplace=True)
    return df


#this is the entry point
@functions_framework.cloud_event
def trigger_pubsub(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    ################
    # Preparations #
    ################
    # todo: refactor this into main() function for gcp

    # Parse config
    config = configparser.ConfigParser()
    # set bucket to None, so it's not undefined
    bucket_name = os.environ.get("GCP_BUCKET_NAME", None)


    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob("config.ini")
    config_content = blob.download_as_text()
    config.read_string(config_content)

    SEARCH_TERM = config.get('Standard', 'SEARCH_TERM')
    SEARCH = config.getboolean('Standard', 'SEARCH')
    MAX_RESULTS = config.getint('Standard', 'MAX_RESULTS')
    UPDATE = config.getboolean('Standard', 'UPDATE')
    BASE_FILENAME = config.get('Standard', 'BASE_FILENAME')
    DIRECTORY = config.get('Standard', 'DIRECTORY')
    CONSOLE_LOG = config.getboolean('Advanced', 'CONSOLE_LOG')
    LOG_RETURNS = config.getboolean('Advanced', 'LOG_RETURNS')
    NEWSTATS_DAY = config.getint('Advanced', 'NEWSTATS_DAY')
    NEWOUTPUT_WEEKDAY = config.get('Advanced', 'NEWOUTPUT_WEEKDAY')
    SECRET_NAME = config.get('Advanced', 'GCP_SECRET')

    # Logging
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

    PARAMETERS = [SEARCH_TERM,
                  SEARCH,
                  MAX_RESULTS,
                  UPDATE,
                  BASE_FILENAME,
                  DIRECTORY,
                  CONSOLE_LOG,
                  LOG_RETURNS,
                  NEWOUTPUT_WEEKDAY,
                  NEWSTATS_DAY,
                  ]
    for parameter in PARAMETERS:
        if parameter == "":
            logging.warning(f"Parameter {parameter} not set!")

    # Youtube API

    # silence google api warnings
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

    # use gcp secret manager to get the youtube api key (save api key as a secret and copy path to config.ini
    client = secretmanager.SecretManagerServiceClient()
    secret_version = client.access_secret_version(name=SECRET_NAME)
    # collect parameters for API call
    DEVELOPER_KEY = secret_version.payload.data.decode("UTF-8")
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    #API call
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
    ####################################################################################################################
    # rename file in regular intervals to avoid extreme file sizes
    # todo: refactor this to safe it into a database
    if bucket_name:
        rename_cloud_storage_blobs(bucket_name, BASE_FILENAME, NEWOUTPUT_WEEKDAY, NEWSTATS_DAY)
        old_df = load_data_from_bucket(bucket, f'output/{BASE_FILENAME}-output.csv')

    # start here
    if SEARCH:
        yt_ids = youtube_search(SEARCH_TERM, MAX_RESULTS, client=youtube)
    else:
        try:
            yt_ids = '\n'.join(old_df.index.levels[1])
        except Exception:
            try:
                # todo: change this so it also works on gcp - i.e. load from blob
                logging.info('Getting youtube IDs from yt_ids.csv...')
                yt_ids = pd.read_csv(os.path.join(save_dir, 'yt_ids.csv'),
                                     encoding='utf-8').to_string(index=False)
                logging.info('...done')

            except Exception:
                logging.warning('There is no old data available. Please run script again with SEARCH = True.')
                yt_ids = None
                exit(1)
    try:
        yt_ids = load_ids(save_dir, yt_ids)

    except Exception:
        logging.info('No yt_id list available. Continuing with results from search / results from old data.')

    if UPDATE and yt_ids is not None:
        new_df = get_youtube_data(yt_ids.replace('\n', ','), youtube)
        if old_df is not None:
            final_df = pd.concat([old_df, new_df], axis=0, join='inner')
            final_df.drop_duplicates(inplace=True)        else:
            final_df = new_df
    else:
        final_df = old_df
        new_df = old_df
    try:
        #todo: change for use on gcp
        old_stats_df = load_data(os.path.join(save_dir, f'{BASE_FILENAME}-statistics.csv'), ['Date', 'Metric'])
        old_stats_df = load_data_from_bucket(bucket, f'output/{BASE_FILENAME}-statistics.csv', ['Date', 'Metric'])

    except Exception:
        logging.WARNING("old -statistics file can't be opened!")
        old_stats_df = None

    if old_stats_df is not None and UPDATE:
        new_stats_df = calc_stats(new_df)
        final_stats_df = pd.concat([old_stats_df, new_stats_df], axis=0, join='inner')

    elif UPDATE:
        new_stats_df = calc_stats(new_df)
        final_stats_df = new_stats_df

    elif old_stats_df is not None:
        final_stats_df = old_stats_df

    else:
        logging.warning('Can not calculate stats without data. Run the script at least once with UPDATE = True!')
        final_stats_df = None
        exit(1)

        # save data
    logging.info('Saving data ...')

    # Save Data to GCP bucket
    blob_name_output = f'output/{BASE_FILENAME}-output.csv'  # Name of the CSV file in the bucket
    blob_name_stats = f'stats/{BASE_FILENAME}-statistics.csv'  # Name of the CSV file in the bucket

    with storage_client.bucket(bucket_name=bucket_name).blob(blob_name_output).open("w") as file:
        final_df.to_csv(file, sep=';', encoding='utf-8', index=False)
    with storage_client.bucket(bucket_name=bucket_name).blob(blob_name_stats).open("w") as file:
        final_stats_df.to_csv(file, sep=';', encoding='utf-8', index=False)