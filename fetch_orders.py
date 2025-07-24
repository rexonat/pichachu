import os
import json
import csv
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta

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

    # If credentials are invalid, refresh them (though service accounts typically don't expire)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid credentials found.")
            return None

    return build('drive', 'v3', credentials=creds)

def upload_file_to_gdrive(file_path):
    """Upload the file to Google Drive."""
    service = authenticate_gdrive()

    if service:
        # Specify the folder ID here (replace with your actual folder ID)
        folder_id = '1jMO6rq2HfQr1zjiDZxaYI7ew4WPctFLX'  # Replace with the folder ID where you want to upload

        file_metadata = {
            'name': 'orders.csv',  # The file name on Google Drive
            'parents': [folder_id]  # Specify the folder ID here
        }

        media = MediaFileUpload(file_path, mimetype='text/csv')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        print(f"✅ File uploaded to Google Drive with ID: {file['id']} in folder {folder_id}")
    else:
        print("Google Drive authentication failed, unable to upload file.")

def get_orders():
    """Fetch orders from Royal Mail API."""
    url = "https://api.parcel.royalmail.com/api/v1/orders"
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "Accept": "application/json",
    }
    params = {
        "pageSize": 30,  # Adjust to get more or fewer orders
        "startDateTime": (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%S'),  # Last 30 days
        "endDateTime": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
    }
    
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"❌ Error fetching data: {response.status_code}, {response.text}")
        return []
    
    data = response.json()
    orders = data.get("orders", [])
    print(f"Fetched {len(orders)} orders.")
    return orders

def save_orders_to_csv(orders, path="orders.csv"):
    """Save the fetched orders to a CSV file."""
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "customer", "package format", "shipping service", "tracking", "status"])
        for order in orders:
            writer.writerow([
                order.get("orderDate", ""),
                order.get("customerName", ""),
                order.get("packageFormat", ""),
                order.get("shippingServiceUsed", ""),
                order.get("trackingNumber", ""),
                order.get("status", "")
            ])
    print(f"✅ Saved {len(orders)} orders to: {path}")

if __name__ == "__main__":
    try:
        # Step 1: Fetch orders from Royal Mail
        orders = get_orders()

        # Step 2: Save orders to CSV
        if orders:
            save_orders_to_csv(orders)

            # Step 3: Upload the CSV file to Google Drive
            upload_file_to_gdrive("orders.csv")
        else:
            print("No orders to process.")
    except Exception as e:
        print(f"An error occurred: {e}")


