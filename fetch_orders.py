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

    # If credentials are expired, refresh them
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())  # Refresh the credentials
            print("Credentials successfully refreshed.")  # Debugging log
        except Exception as e:
            print(f"Failed to refresh credentials: {e}")
            return None
    elif not creds.valid:
        print("Credentials are invalid.")  # Debugging log
        return None

    # Return the authenticated service
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        return drive_service
    except Exception as e:
        print(f"Error creating the Drive service: {e}")
        return None


