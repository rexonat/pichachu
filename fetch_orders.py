import os
import json
from google.auth.transport.requests import Request
from google.auth.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API authentication
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_gdrive():
    """Authenticate the user to Google Drive API using credentials stored in an environment variable."""
    creds = None

    # Retrieve the credentials from the environment variable
    google_credentials = os.getenv("GOOGLE_CREDENTIALS")

    if google_credentials:
        # Parse the JSON string into a dictionary
        creds_dict = json.loads(google_credentials)

        # Create credentials object from the dictionary
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        print("No credentials found in environment variables.")
        return None

    # If no credentials or they are invalid, re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid credentials found.")
            # You can implement an interactive login here if needed

    return build('drive', 'v3', credentials=creds)

def upload_file_to_gdrive(file_path):
    """Upload the file to Google Drive."""
    service = authenticate_gdrive()

    if service:
        file_metadata = {
            'name': 'orders.csv',  # The file name on Google Drive
        }
        media = MediaFileUpload(file_path, mimetype='text/csv')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        print(f"✅ File uploaded to Google Drive with ID: {file['id']}")
    else:
        print("Google Drive authentication failed, unable to upload file.")

# Rest of your script continues as normal...
