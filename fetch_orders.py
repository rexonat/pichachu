import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

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

    # Return the authenticated service
    return build('drive', 'v3', credentials=creds)

if __name__ == "__main__":
    try:
        # Step 1: Try to authenticate with Google Drive
        service = authenticate_gdrive()

        if service:
            print("Successfully authenticated and connected to Google Drive.")
        else:
            print("Failed to authenticate with Google Drive.")
    except Exception as e:
        print(f"An error occurred: {e}")

