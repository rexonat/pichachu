import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Google Drive API authentication
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_gdrive():
    """Authenticate using service account credentials stored in environment variable."""
    creds = None

    # Retrieve the credentials from the environment variable
    google_credentials = os.getenv("GOOGLE_CREDENTIALS")

    if google_credentials:
        try:
            # Parse the JSON string into a dictionary
            creds_dict = json.loads(google_credentials)

            # Create credentials object from the dictionary using the service account
            creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            print("Google Drive authentication successful.")  # Debugging log

        except Exception as e:
            print(f"Failed to load credentials: {e}")
            return None
    else:
        print("GOOGLE_CREDENTIALS environment variable is missing.")
        return None

    # Check if the credentials are valid
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        print("Credentials refreshed.")  # Debugging log
    elif not creds.valid:
        print("Credentials are invalid or expired.")  # Debugging log
        return None

    # Return the authenticated service
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        return drive_service
    except Exception as e:
        print(f"Error creating the Drive service: {e}")
        return None

def test_google_drive_service():
    """Test the Google Drive service connection by listing files in the root directory."""
    service = authenticate_gdrive()

    if service:
        # List files in the Google Drive root folder to test the connection
        try:
            results = service.files().list(fields="files(id, name)").execute()
            items = results.get('files', [])
            if not items:
                print("No files found in Google Drive.")
            else:
                print("Files in Google Drive:")
                for item in items:
                    print(f"{item['name']} (ID: {item['id']})")
        except Exception as e:
            print(f"Error listing files: {e}")
    else:
        print("Google Drive service is not available.")

if __name__ == "__main__":
    test_google_drive_service()

