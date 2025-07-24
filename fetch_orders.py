def check_folder_permissions(service, folder_id):
    """Check if the service account has access to the folder."""
    try:
        # List the files in the folder to confirm access
        results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print("Folder is empty or inaccessible.")
        else:
            print(f"Files in folder {folder_id}:")
            for item in items:
                print(f"File name: {item['name']}, File ID: {item['id']}")
    except Exception as e:
        print(f"Error accessing folder: {e}")

# Example usage (call after authentication)
service = authenticate_gdrive()
check_folder_permissions(service, '1jMO6rq2HfQr1zjiDZxaYI7ew4WPctFLX')  # Replace with your folder ID

