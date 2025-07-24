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

    # Debug log to check initial credentials validity
    print(f"Initial credentials valid: {creds.valid}")
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

    # Debug log to check credentials after refresh
    print(f"Credentials after refresh valid: {creds.valid}")

    # Return the authenticated service
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        print("Google Drive service created successfully.")  # Debugging log
        return drive_service
    except Exception as e:
        print(f"Error creating the Drive service: {e}")
        return None


