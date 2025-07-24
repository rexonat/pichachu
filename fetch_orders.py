import os
import requests
import csv
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

print("🚀 Starting Royal Mail order fetch")

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.parcel.royalmail.com/api/v1/orders/export"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}
OUTPUT_FILE = "/tmp/orders.csv"


def get_orders(last_days=30):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=last_days)

    params = {
        "pageSize": 100,
        "startDateTime": start.isoformat(),
        "endDateTime": now.isoformat()
    }

    all_orders = []
    continuation_token = None

    while True:
        if continuation_token:
            params["continuationToken"] = continuation_token

        print(f"📡 Requesting: {BASE_URL}")
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        print(f"🔁 Response Status: {response.status_code}")
        response.raise_for_status()

        data = response.json()
        orders = data.get("orders", [])
        print(f"📦 Retrieved {len(orders)} orders")
        all_orders.extend(orders)

        continuation_token = data.get("continuationToken")
        if not continuation_token:
            break

    return all_orders


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
    print(f"✅ Saved {len(orders)} orders to {path}")


if __name__ == "__main__":
    try:
        orders = get_orders(last_days=30)
        save_orders_to_csv(orders)
    except Exception as e:
        print(f"❌ Error: {e}")

