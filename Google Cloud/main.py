import base64
import datetime
import os
import copy

import functions_framework
import pandas as pd
from google.cloud import storage, secretmanager, bigquery
from googleapiclient.discovery import build
from io import StringIO
import pandas_gbq


def youtube_search(search_term, max_results, client):
    """
    Returns the IDs of videos (as \n separated string) that fit a certain search term
    :param search_term: The term to search for
    :param max_results: Maximum number of search results to consider
    :param client: youtube API client
    :return: \n separated list of YouTube IDs
    """
    print("Searching YouTube..")
    SEARCH_TERM = copy.copy(search_term)  # seperates the term from the actual search string
    search_term = f"{search_term}|{search_term}Salon|{search_term}Youth|{search_term}Studio"
    if max_results > 50:
        search_response = client.search().list(
            q=search_term,
            maxResults=50,
            part='id,snippet',
            type='video',
            channelId='UCsT0YIqwnpJCM-mx7-gSA4Q'
        ).execute()

        videos = []
        for search_result in search_response.get('items', []):
            if SEARCH_TERM.upper() in search_result['snippet']['title'].upper():
                videos.append(search_result['id']['videoId'])

        token = search_response.get('nextPageToken', None)
        remaining_results = max_results - 50
        resultsPerPage = search_response.get('pageInfo')['resultsPerPage']

        while token is not None and remaining_results > 50 and resultsPerPage > 0:
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
                    print('Found new video: ' + search_result['snippet']['title'])
                else:
                    print('Discarded video: ' + search_result['snippet']['title'])
                    discard_counter += 1

            print(f'Discarded video count:{discard_counter}')

            token = search_response.get('nextPageToken', None)
            remaining_results = max_results - 50
            resultsPerPage = search_response.get('pageInfo')['resultsPerPage']
            print(f'ResultsPerPage:{resultsPerPage}')

    else:
        search_response = client.search().list(
            q=search_term,
            maxResults=max_results,
            part='id,snippet',
            type='video',
            channelId='UCsT0YIqwnpJCM-mx7-gSA4Q'
        ).execute()
        videos = []

        for search_result in search_response.get('items', []):
            if 'TEDXTUM' in search_result['snippet']['title'].upper():
                videos.append(search_result['id']['videoId'])

    return '\n'.join(videos)


def get_youtube_data(ids_str, client):
    """
    Get YouTube data from a list of video IDs
    :param ids_str: YouTube IDs of all videos to be analysed, comma separated
    :param client: YouTube client (from youtube API)
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

        date = datetime.datetime.now().date()

        for result in response.get('items', []):

            title = result['snippet']['title']
            if '|' in title:
                from_title = [x.strip() for x in title.split('|')]

                title = from_title[0]
                speaker = from_title[1]
                # tedx = from_title[2]
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


def load_ids(bucket, blob_name, searched_ids):
    """
    Loads YouTube IDs from 'yt_ids.csv' in directory and concats it with searched_ids (result from yt search)
    :param bucket: directory where yt_ids is located
    :param blob_name: blob/filename where yt ids are saved
    :param searched_ids: result from yt search: \n separated string of yt ids
    :return: \n separated string of yt IDs that are either in the file or in the list from yt search
    """
    print("Loading IDs...")
    blob = bucket.blob(blob_name)
    saved_ids = pd.read_csv(StringIO(blob.download_as_text()),
                            encoding='utf-8').to_string(index=False)
    if searched_ids is not None:
        searched_ids_list = searched_ids.split('\n')
        saved_ids_list = saved_ids.split('\n')
        for item in saved_ids_list:
            if item not in searched_ids_list:
                searched_ids_list.append(item)
    else:
        print(f"No searched IDs available. Using IDs from {blob}.")
        searched_ids_list = saved_ids.split('\n')

    print("... done")
    return '\n'.join(searched_ids_list)


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
        new_output_blob_name = f'output/{BASE_FILENAME}-output_{today.isocalendar()[0]}' \
                               f'_week{today.isocalendar()[1]}.csv'
        old_output_blob = bucket.blob(f'output/{BASE_FILENAME}-output.csv')
        bucket.rename_blob(old_output_blob, new_output_blob_name)

    if today.day == NEWSTATS_DAY:
        new_stats_blob_name = f'stats/{BASE_FILENAME}-statistics_{today.isocalendar()[1]}_{today.month}.csv'
        old_stats_blob = bucket.blob(f'stats/{BASE_FILENAME}-statistics.csv')
        bucket.rename_blob(old_stats_blob, new_stats_blob_name)


def load_data_from_bucket(bucket_name, blob_name, indices):
    """
    Loads previously saved data from bucket
    :param bucket_name: name of the bucket the csv is in
    :param blob_name: name of the .csv file containing earlier search results
    :param indices: the name of the indices that will be set in the resulting data frame
    :return: Dataframe with earlier search results and the indicated indices
    """

    print("Loading data from bucket")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    try:
        data = blob.download_as_text()
    except Exception as e:
        print(e)

    print(f'data type of data{type(data)}')
    data_io = StringIO(data)
    df = pd.read_csv(data_io, sep=';', encoding='utf-8', parse_dates=['Date'])
    df.set_index(indices, inplace=True)
    print(df)
    print("..done")
    return df


# this is the entry point for the cloud function
@functions_framework.cloud_event
def trigger_pubsub(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    print(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
    search_update = base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8')

    ################
    # Preparations #
    ################

    # get bucket name from environment variables
    bucket_name = os.environ.get("GCP_BUCKET_NAME", None)
    print(f"Bucket {bucket_name}")
    # set up storage client
    storage_client = storage.Client()


    # Get Config from environment variables!
    SEARCH_TERM = os.environ.get("SEARCH_TERM", "SEARCH_TERM is not set")
    SEARCH = bool(os.environ.get("SEARCH", "SEARCH is not set"))
    MAX_RESULTS = int(os.environ.get("MAX_RESULTS", "MAX_RESULTS is not set"))
    UPDATE = bool(os.environ.get("UPDATE", "UPDATE is not set"))
    BASE_FILENAME = os.environ.get("BASE_FILENAME", "BASE_FILENAME is not set")
    NEWSTATS_DAY = int(os.environ.get("NEWSTATS_DAY", "NEWSTATS_DAY is not set"))
    NEWOUTPUT_WEEKDAY = os.environ.get("NEWOUTPUT_WEEKDAY", "NEWOUTPUT_WEEKDAY is not set")
    SECRET_NAME = os.environ.get("GCP_SECRET", "GCP_SECRET is not set")

    # check if pubsub topic sends search or update
    if search_update == "search":
        SEARCH = True
    elif search_update == "update":
        UPDATE = True
        SEARCH = False
    print(f"Search:{SEARCH}")
    print(f"Update:{UPDATE}")

    print(f"environment variables: {os.environ}")

    # YouTube API

    # use gcp secret manager to get the YouTube api key
    client = secretmanager.SecretManagerServiceClient()
    secret_version = client.access_secret_version(name=SECRET_NAME)
    # collect parameters for API call
    DEVELOPER_KEY = secret_version.payload.data.decode("UTF-8")
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    # API call
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
    ####################################################################################################################
    # rename file in regular intervals to avoid extreme file sizes

    if bucket_name:
        try:
            rename_cloud_storage_blobs(bucket_name, BASE_FILENAME, NEWOUTPUT_WEEKDAY, NEWSTATS_DAY)
            old_df = load_data_from_bucket(bucket_name, f'output/{BASE_FILENAME}-output.csv', ['Date', 'ID']) # get old data
        except Exception:
            old_df = None

    if SEARCH:
        yt_ids = youtube_search(SEARCH_TERM, MAX_RESULTS, client=youtube)
        print("...complete")
    else:
        try:
            yt_ids = '\n'.join(old_df.index.levels[1])
        except Exception:
            try:
                bucket = storage_client.bucket(bucket_name)
                yt_ids = load_ids(bucket, 'yt_ids.csv', None)

            except Exception:
                yt_ids = None
                exit(1)
    try:
        bucket = storage_client.bucket(bucket_name)
        yt_ids = load_ids(bucket, 'yt_ids.csv', yt_ids)
    except Exception as e:
        print('No yt_id list available. Continuing with results from search / results from old data.')
        print(e)

    if UPDATE and yt_ids is not None:
        print("Updating values..")
        new_df = get_youtube_data(yt_ids.replace('\n', ','), youtube)  # todo: check if leftover "ID" causes problems
        print("...done.")

        if old_df is not None:
            final_df = pd.concat([old_df, new_df], axis=0, join='inner')
            final_df.drop_duplicates(inplace=True)
        else:
            final_df = new_df
        print(new_df)
    else:
        final_df = old_df
        new_df = old_df
    try:
        old_stats_df = load_data_from_bucket(bucket_name, f'output/{BASE_FILENAME}-statistics.csv', ['Date', 'Metric'])

    except Exception:
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
        final_stats_df = None
        exit(1)
    print("...done")
    # Save Data to GCP bucket
    print(f"Saving to {BASE_FILENAME}")
    blob_name_output = f'output/{BASE_FILENAME}-output.csv'  # Name of the CSV file in the bucket
    blob_name_stats = f'stats/{BASE_FILENAME}-statistics.csv'  # Name of the CSV file in the bucket

    # Save to csv
    with storage_client.bucket(bucket_name=bucket_name).blob(blob_name_output).open("w") as file:
        final_df.to_csv(file, sep=';', encoding='utf-8', index=True)
    with storage_client.bucket(bucket_name=bucket_name).blob(blob_name_stats).open("w") as file:
        final_stats_df.to_csv(file, sep=';', encoding='utf-8', index=True)

    # Save Data to BigQuery
    all_table_id = os.environ.get("ALLTABLE")
    stats_table_id = os.environ.get("STATSTABLE")

    # Manually cast datatypes to fit BigQuery table Schema
    for stat in ['Views', 'Likes', 'Dislikes', 'Favourite Count', 'Comment Count']:
        try:
            new_df[stat] = new_df[stat].astype('int64')
            print(new_df[stat])
        except ValueError as e:
            print(f"Error converting {stat} column to int64: {e}")

    for stat in ['Views', 'Likes', 'Dislikes', 'Favourite Count', 'Comment Count']:
        try:
            new_stats_df[stat] = new_stats_df[stat].astype('float64')
        except ValueError as e:
            print(f"Error converting {stat} column to int64: {e}")

    # Collapse multi-index
    new_df.reset_index(inplace=True)
    new_stats_df.reset_index(inplace=True)

    # Convert to datetime objects that fit BigQuery Schema
    new_df['Date'] = pd.to_datetime(new_df['Date']).dt.date
    new_stats_df['Date'] = pd.to_datetime(new_stats_df['Date']).dt.date

    new_df['Published on'] = pd.to_datetime(new_df['Published on'])

    # Convert indices to fit BigQuery Schema
    new_df.columns = [col.replace(' ', '_') for col in new_df.columns]
    new_stats_df.columns = [col.replace(' ', '_') for col in new_stats_df.columns]

    print(f'Data Types: \n new_df: {new_df.dtypes}\n new_stats_df {new_stats_df.dtypes}')



    # Set up Schemata
    all_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=[
        bigquery.SchemaField("Date", "DATE"),
        bigquery.SchemaField("ID", "STRING"),
        bigquery.SchemaField("Title", "STRING"),
        bigquery.SchemaField("Speaker_Name", "STRING"),
        bigquery.SchemaField("Thumbnail", "STRING"),
        bigquery.SchemaField("Tags", "STRING"),
        bigquery.SchemaField("Views", "INTEGER"),
        bigquery.SchemaField("Likes", "INTEGER"),
        bigquery.SchemaField("Dislikes", "INTEGER"),
        bigquery.SchemaField("Favourite_Count", "INTEGER"),
        bigquery.SchemaField("Comment_Count", "INTEGER"),
        bigquery.SchemaField("Published_on", "TIMESTAMP"),

    ]
    )

    stats_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=[
        bigquery.SchemaField("Date", "DATE"),
        bigquery.SchemaField("Metric", "STRING"),
        bigquery.SchemaField("Views", "FLOAT"),
        bigquery.SchemaField("Likes", "FLOAT"),
        bigquery.SchemaField("Dislikes", "FLOAT"),
        bigquery.SchemaField("Favourite_Count", "FLOAT"),
        bigquery.SchemaField("Comment_Count", "FLOAT"),

    ]
    )

    bqclient = bigquery.Client()

    try:
        print("appending output data")
        all_job = bqclient.load_table_from_dataframe(new_df, all_table_id, job_config=all_config)
        all_job.result()
        print("...done")
    except Exception as e:
        print(e)
        print(f"BigQuery Table {all_table_id} does not exist or cannot be created.")
    try:
        print("appending stats data")
        stats_job = bqclient.load_table_from_dataframe(new_stats_df, stats_table_id, job_config=stats_config)
        stats_job.result()
        print("...done")
    except Exception as e:
        print(e)
        print(f"BigQuery Table {stats_table_id} does not exist or cannot be created.")
