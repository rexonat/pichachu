import os
import json
import csv
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Google Drive API authentication
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_gdrive():
    """Authenticate using service account credentials stored in environment variable."""
    creds = None
    print("Starting Google Drive authentication...")

    # Retrieve the credentials from the environment variable
    google_credentials = os.getenv("GOOGLE_CREDENTIALS")
    if not google_credentials:
        print("GOOGLE_CREDENTIALS environment variable is missing.")
        return None

    try:
        # Parse the JSON string into a dictionary
        creds_dict = json.loads(google_credentials)
        print("Successfully parsed credentials.")  # Debugging log

        # Create credentials object from the dictionary using the service account
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        print("Google Drive authentication successful.")  # Debugging log

    except Exception as e:
        print(f"Failed to load credentials: {e}")
        return None

    # Check if credentials are expired and refresh them
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())  # Refresh the credentials
            print("Credentials successfully refreshed.")  # Debugging log
        except Exception as e:
            print(f"Failed to refresh credentials: {e}")
            return None
    elif not creds.valid:
        print("Credentials are invalid.")
        return None

    # Return the authenticated service
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        print("Google Drive service created successfully.")  # Debugging log
        return drive_service
    except Exception as e:
        print(f"Error creating the Drive service: {e}")
        return None


def create_random_csv(file_path="random_data.csv"):
    """Create a random CSV file."""
    print(f"Creating a random CSV file: {file_path}")
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Age", "Score"])  # Writing header
        for i in range(1, 11):  # Creating 10 rows of random data
            writer.writerow([i, f"Name_{i}", random.randint(18, 60), random.randint(50, 100)])
    print(f"Random CSV file created: {file_path}")


def upload_file_to_gdrive(file_path):
    """Upload the file to Google Drive."""
    service = authenticate_gdrive()

    if service:
        try:
            folder_id = '1AdrR-SRK11GNxoAfs5cpr9NKSNgHf8I1'  # Replace with your folder ID

            file_metadata = {
                'name': 'random_data.csv',  # File name in Google Drive
                'parents': [folder_id]  # Folder ID where the file should go
            }

            media = MediaFileUpload(file_path, mimetype='text/csv')
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            print(f"✅ File uploaded to Google Drive with ID: {file['id']} in folder {folder_id}")

        except Exception as e:
            print(f"Error uploading file to Google Drive: {e}")
    else:
        print("Google Drive authentication failed, unable to upload file.")


if __name__ == "__main__":
    try:
        # Step 1: Create a random CSV file
        create_random_csv()

        # Step 2: Upload the random CSV file to Google Drive
        upload_file_to_gdrive("random_data.csv")

    except Exception as e:
        print(f"An error occurred: {e}")

