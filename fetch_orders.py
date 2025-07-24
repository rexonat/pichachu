import requests
import csv
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables (e.g., API_KEY)
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.parcel.royalmail.com/api/v1"
OUTPUT_FILE = "/tmp/orders.csv"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

def get_orders():
    # Setting query parameters
    params = {
        "pageSize": 30,  # Adjust to get more or fewer orders
        "startDateTime": (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%S'),  # Last 30 days
        "endDateTime": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
    }
    
    url = f"{BASE_URL}/orders"
    
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
        orders = get_orders()
        save_orders_to_csv(orders)
    except Exception as e:
        print(f"An error occurred: {e}")
