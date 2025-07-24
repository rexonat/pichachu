import requests
import csv
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load environment variables (e.g., API_KEY)
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.parcel.royalmail.com/api/v1"
OUTPUT_FILE = "/tmp/orders.csv"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

# Google Drive API authentication
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_gdrive():
    """Authenticate the user to Google Drive API."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def upload_file_to_gdrive(file_path):
    """Upload the file to Google Drive."""
    service = authenticate_gdrive()

    file_metadata = {
        'name': 'orders.csv',  # The file name on Google Drive
    }
    media = MediaFileUpload(file_path, mimetype='text/csv')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    print(f"✅ File uploaded to Google Drive with ID: {file['id']}")

def get_orders():
    url = f"{BASE_URL}/orders"
    params = {
        "pageSize": 30,  # Adjust to get more or fewer orders
        "startDateTime": (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%S'),  # Last 30 days
        "endDateTime": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
    }
    
    print(f"Requesting URL: {url}")
    print(f"With Headers: {HEADERS}")
    print(f"With Params: {params}")
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}, {response.text}")
        response.raise_for_status()
    
    data = response.json()
    orders = data.get("orders", [])
    print(f"Fetched {len(orders)} orders.")
    return orders

def save_orders_to_csv(orders, path=OUTPUT_FILE):
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
        # Fetch orders from Royal Mail API
        orders = get_orders()
        
        # Save orders to CSV
        save_orders_to_csv(orders)
        
        # Upload the CSV file to Google Drive
        upload_file_to_gdrive(OUTPUT_FILE)
    
    except Exception as e:
        print(f"An error occurred: {e}")
