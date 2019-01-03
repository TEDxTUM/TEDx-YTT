from googleapiclient.discovery import build
import pandas as pd
import logging
import sys
import argparse
import configparser
import datetime
from argparse import RawTextHelpFormatter
import os


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
    Returns the IDs of videos (as \n separeted string) that fit a certain search term
    :param search_term: The term to search for
    :param max_results: Maximum number of search results to consider.
    :param client: youtube API client
    :return: \n separated list of youtube IDs
    """

    if max_results > 50:
        search_response = client.search().list(
            q=f'{search_term}*',
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

        while token is not None and remaining_results > 50:
            search_response = client.search().list(
                q=f'{search_term}*',
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

    for id in ids_str.split(','):
        response = client.videos().list(
            part='id,'
                 'snippet,'
                 ' statistics',
            id=id,
        ).execute()

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
    logging.info(f'Loading old data from {filename}')
    try:
        df = pd.read_csv(filename, sep=';', encoding='utf-8', parse_dates=['Date'])
        df.set_index(indices, inplace=True)
    except FileNotFoundError:
        logging.warning(f'File {filename} does not exist! Continuing without loading old data.')
        df = None

    logging.info(f'...done!')
    return df


@trace
def load_ids(directory, searched_ids):
    """
    Loads youtube IDs from 'yt_ids.csv' in directory and concats it with searched_ids (result from yt search)
    :param directory: directory where yt_ids is located
    :param searched_ids: result from yt search: \n seperated string of yt ids
    :return: \n separeted string of yt IDs that are either in the file or in the list from yt search
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

    dates = []
    date = datetime.datetime.now().date()
    described = df_copy.astype('float64').describe(include='all')

    for row in range(0, described.shape[0]):
        dates.append(date)

    described['Date'] = dates
    described.reset_index(inplace=True)

    described.rename(columns={'index': 'Metric'}, inplace=True)

    described.set_index(['Date', 'Metric'], inplace=True)

    return described.round()


if __name__ == '__main__':
   ################
   # Preparations #
   ################

    # silence logging exceptions
    logging.raiseExceptions = False

    # Parse config
    config = configparser.ConfigParser()
    config.read(os.path.join(sys.path[0], 'config.ini'))

    SEARCH_TERM = config.get('Standard', 'SEARCH_TERM')
    SEARCH = config.getboolean('Standard', 'SEARCH')
    MAX_RESULTS = config.getint('Standard', 'MAX_RESULTS')
    UPDATE = config.getboolean('Standard', 'UPDATE')
    BASE_FILENAME = config.get('Standard', 'BASE_FILENAME')
    DIRECTORY = config.get('Standard', 'DIRECTORY')
    CONSOLE_LOG = config.getboolean('Advanced', 'CONSOLE_LOG')
    LOG_RETURNS = config.getboolean('Advanced', 'LOG_RETURNS')
    NEWOUTPUT_WEEKDAY = config.get('Advanced', 'NEWOUTPUT_WEEKDAY')
    NEWSTATS_DAY = config.getint('Advanced', 'NEWSTATS_DAY')

    # Parse args
    parser = argparse.ArgumentParser(description='Search for a TEDx on youtube and '
                                                 'return stats to all videos with that TEDx in title.\n'
                                                 'Current arguments are:\n'
                                                 f'SEARCH_TERM = \t{SEARCH_TERM}\n'
                                                 f'SEARCH = \t{SEARCH}\n'
                                                 f'MAX_RESULTS = \t{SEARCH}\n'
                                                 f'UPDATE = \t{UPDATE}\n'
                                                 f'BASE_FILENAME = {BASE_FILENAME}\n'
                                                 f'CONSOLE_LOG = \t{CONSOLE_LOG}\n'
                                                 f'DIRECTORY = \t{DIRECTORY}\n',

                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('-q', '--search_term', help='Term to search for - your TEDx\'s name', type=str)
    parser.add_argument('-s', '--search', help='Switch searching for new videos on/off', type=bool)
    parser.add_argument('-m', '--max_results', help='Number of search results used from search request.', type=int)
    parser.add_argument('-u', '--update', help='Switch updating statistics on/off', type=bool)
    parser.add_argument('-f', '--base_filename', help='Base filename for output files', type=str)
    parser.add_argument('-l', '--console_log', help='Switch logging output to python console on/off', type=bool)
    parser.add_argument('-r', '--log_return', help='Switch output of functions in console on/off', type=bool)
    parser.add_argument('-d', '--directory', help='Directory where the output should be saved to', type=str)
    parser.add_argument('-no', '--newoutput_weekday', help='weekday at which -output file is renamed', type=str)
    parser.add_argument('-ns', '--newstats_day', help='Day of the month at which -statistics file is renamed', type=int)
    args = parser.parse_args()

    if args.search_term:
        SEARCH_TERM = args.search_term
    if args.search:
        SEARCH = args.search
    if args.max_results:
        MAX_RESULTS = args.max_results
    if args.update:
        UPDATE = args.update
    if args.base_filename:
        BASE_FILENAME = args.search_term
    if args.console_log:
        CONSOLE_LOG = args.search_term
    if args.log_return:
        LOG_RETURNS = args.log_return
    if args.directory:
        DIRECTORY = args.directory
    if args.newoutput_weekday:
        NEWOUTPUT_WEEKDAY = args.newoutput_weekday
    if args.newstats_day:
        NEWSTATS_DAY = args.newstats_day

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

    # get directory where the data is saved
    if DIRECTORY == 'current':
        save_dir = os.getcwd()
    else:
        save_dir = os.path.abspath(os.sep)
        rel_dir = DIRECTORY.split('/')
        for string in rel_dir:
            if string != '':
                save_dir = os.path.join(save_dir, string)

    logging.info(f'Save directory: {save_dir}')

    # Youtube API

    # silence google api warnings
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

    with open(os.path.join(sys.path[0], 'yapi.txt')) as file:
        DEVELOPER_KEY = file.read()

    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)


    ####################################################################################################################


    old_df = load_data(os.path.join(save_dir, f'{BASE_FILENAME}-output.csv'), ['Date', 'ID'])

    if SEARCH:
        yt_ids = youtube_search(SEARCH_TERM, MAX_RESULTS, client=youtube)
    else:
        try:
            yt_ids = '\n'.join(old_df.index.levels[1])
        except:
            try:
                logging.info('Getting youtube IDs from yt_ids.csv...')
                yt_ids = pd.read_csv(os.path.join(save_dir, 'yt_ids.csv'),
                                     encoding='utf-8').to_string(index=False)
                logging.info('...done')

            except:
                logging.warning('There is no old data available. Please run script again with SEARCH = True.')
                yt_ids = None
                exit(1)
    try:
    #todo: load/save yt_ids from script or data directory?
        yt_ids = load_ids(save_dir, yt_ids)

    except:
        logging.info('No yt_id list available. Continuing with results from search / results from old data.')

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

    old_stats_df = load_data(os.path.join(save_dir, f'{BASE_FILENAME}-statistics.csv'), ['Date', 'Metric'])

    if old_stats_df is not None and UPDATE:
        new_stats_df = calc_stats(new_df)
        final_stats_df = pd.concat([old_stats_df, new_stats_df], axis=0, join='inner')


    elif UPDATE:
        new_stats_df = calc_stats(new_df)
        final_stats_df = new_stats_df

    elif old_stats_df is not None:
        final_stats_df = old_stats_df

    elif UPDATE:
        final_stats_df = calc_stats(new_df)
    else:
        logging.warning('Can not calculate stats without data. Run the script at least once with UPDATE = True!')
        exit(1)

    # save data
    logging.info('Saving data ...')

    final_df.to_csv(os.path.join(save_dir, f'{BASE_FILENAME}-output.csv'), sep=';', encoding='utf-8')
    final_stats_df.to_csv(os.path.join(save_dir, f'{BASE_FILENAME}-statistics.csv'), sep=';', encoding='utf-8')

    final_df.reset_index(inplace=True)
    with open(os.path.join(save_dir, 'yt_ids.csv'), 'w', encoding='utf-8') as file:
        final_df.ID.drop_duplicates(inplace=True)
        final_df.ID.to_csv(file, encoding='utf-8', index=False)

    # rename file in regular intervals to avoid extreme file sizes
    today = datetime.datetime.today()
    weekdays = {"monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4, "friday": 5, "saturday": 6, "sunday": 7}
    if today.isoweekday() == weekdays[NEWOUTPUT_WEEKDAY.lower()]:
        os.rename(os.path.join(save_dir, f'{BASE_FILENAME}-output.csv'), os.path.join(save_dir, f'{BASE_FILENAME}-output_CW{today.isocalendar()[1]}.csv'))
    if today.day == NEWSTATS_DAY:
        os.rename(os.path.join(save_dir, f'{BASE_FILENAME}-statistics.csv'), os.path.join(save_dir,f'{BASE_FILENAME}-statistics_{today.month}.csv'))

    logging.info(f'...done!')
    # write config
    logging.info('Saving config ...')
    cfgfile = open('config.ini', 'w')
    config.write(cfgfile)
    cfgfile.close()

    logging.info(f'...done!')

    logging.info('Checking date and renaming file')

    logging.info('Done with everything!')
