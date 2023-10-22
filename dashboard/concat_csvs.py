import pandas as pd
import glob
import os


# todo: encapsulate this and run the function at the end of tedx-ytt to always get an all_data.csv that works :)
def run_locally(path, filename):
    """
    Function that concats all existing stats or output files and saves the resulting csv LOCALLY
    :param path: rawstring representing the path to stats / output files (use r'this/location/on/machine')
    :param name: filename including .csv of the resulting concated file
    :return:
    """

    all_files = glob.glob(f"{path}/*.csv")
    li = []

    for f in all_files:
        df = pd.read_csv(f, sep=";")
        df = df.drop_duplicates()
        li.append(df)

    data = pd.concat(li, axis=0, ignore_index=True)
    data["Date"] = pd.to_datetime(data["Date"])
    data.sort_values(by="Date", inplace=True)
    data.set_index("Date", inplace=True)
    data.to_csv(filename, sep=";")

def run_on_gcp(folder_path, filename):
    """
    Function that concats all existing stats or output files and saves the resulting csv ON GOOGLE CLOUD
    :param folder_path: pre-fix of all files to be concated within the bucket that is safed in
    environment variable GCS_BUCKET_NAME
    :param filename: Name of the resulting *.csv file
    :return:
    """
    # Get bucket name from environment variables
    bucket_name = os.environ.get("GCS_BUCKET_NAME")

    # Prepare GCS Storage Client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_path)

    li = []

    for blob in blobs:
        content = blob.download_as_text()
        df = pd.read_csv(pd.compat.StringIO(content), sep=";")
        df = df.drop_duplicates()
        li.append(df)

    data = pd.concat(li, axis=0, ignore_index=True)
    data["Date"] = pd.to_datetime(data["Date"])
    data.sort_values(by="Date", inplace=True)
    data.set_index("Date", inplace=True)
    data.to_csv(filename, sep=";")

if "GOOGLE_CLOUD_PROJECT" in os.environ:
    run_on_gcp("local/stats", "all_stats.csv")
    run_on_gcp("local/output", "all_data.csv")
else:
    run_locally(r'local/stats', 'all_stats.csv')
    run_locally(r'local/output', 'all_data.csv')

