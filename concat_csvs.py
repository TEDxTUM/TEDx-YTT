import pandas as pd
import glob


# todo: encapsulate this and run the function at the end of tedx-ytt to always get an all_data.csv that works :)
def run_locally():
    # Path to output csv files
    path = r'output'
    all_files = glob.glob(path + "/*.csv")
    li = []

    for f in all_files:
        df = pd.read_csv(f, sep=";")
        df = df.drop_duplicates()
        li.append(df)

    data = pd.concat(li, axis=0, ignore_index=True)
    data["Date"] = pd.to_datetime(data["Date"])
    data.sort_values(by="Date", inplace=True)
    data.set_index("Date", inplace=True)
    data.to_csv('all_data.csv', sep=";")

def run_on_gcp():
    # Get bucket name from environment variables
    bucket_name = os.environ.get("GCS_BUCKET_NAME")

    # Initialize GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Define the path within the bucket
    folder_path = "output"

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
    data.to_csv('all_data.csv', sep=";") # save this to gcp bucket!!!

if "GOOGLE_CLOUD_PROJECT" in os.environ:
    run_on_gcp()
else:
    run_locally()