import json
import pickle
import time
from os import path, makedirs

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Fit scopes
SCOPES = ['https://www.googleapis.com/auth/fitness.body.read', 'https://www.googleapis.com/auth/fitness.body.write']
# Google Fit data type to filter data sources by
DATA_TYPE = "com.google.weight"
# Start and end time in nanoseconds
START_TIME = "0"
END_TIME = time.time_ns()

# Filename to store the token to
ROOT_DIR = path.join(path.dirname(path.abspath(__file__)), "..")
EXPORTS_FOLDER = path.join(ROOT_DIR, "exports")
AUTH_FOLDER = path.join(ROOT_DIR, "auth")
CREDENTIALS_FILE = path.join(AUTH_FOLDER, "credentials.pickle")
SECRETS_FILE = path.join(AUTH_FOLDER, "client_secret.json")


def save_json(name, data):
    makedirs(EXPORTS_FOLDER, exist_ok=True)
    file_name = f"{name}.json"
    full_name = path.join(EXPORTS_FOLDER, file_name)
    with open(full_name, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def save_credentials(creds):
    makedirs(AUTH_FOLDER, exist_ok=True)
    with open(CREDENTIALS_FILE, 'wb') as token:
        pickle.dump(creds, token)


def load_credentials_from_file():
    if path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as token:
            return pickle.load(token)
    return None


def get_token():
    credentials = load_credentials_from_file()
    if not credentials:
        flow = InstalledAppFlow.from_client_secrets_file(SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=54547)
        save_credentials(credentials)
    elif credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_credentials(credentials)
    return credentials


def main():
    """Shows basic usage of the Fitness API."""
    credentials = get_token()

    google_fit_api = build('fitness', 'v1', credentials=credentials)

    datasources = google_fit_api.users().dataSources().list(userId='me', dataTypeName=DATA_TYPE).execute()

    save_json("datasources", datasources)

    for index, datasource in enumerate(datasources['dataSource']):
        try:
            dataset = google_fit_api.users().dataSources(). \
                datasets(). \
                get(userId='me', dataSourceId=datasource, datasetId=f"{START_TIME}-{END_TIME}"). \
                execute()
            save_json(f"dataset{index}", dataset)
        except Exception as e:
            print("Error at " + datasource)
            print(e)


if __name__ == '__main__':
    main()
