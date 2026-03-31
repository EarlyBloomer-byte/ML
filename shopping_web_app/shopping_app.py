import os
import argparse
from datetime import datetime, UTC
from pymongo import MongoClient

# Get MongoDB URI from environment variable
uri = os.environ.get("MONGO_URI")

if not uri:
    raise ValueError("MONGO_URI environment variable not set")

# Connect to MongoDB
client = MongoClient(uri)

# Create / Access Database
db = client["shopping_app_db"]

# Create / Access Collection
shopping_collection = db["shopping_list"]

SAMPLE_ITEMS = [
    {"name": "Rice", "quantity": 2, "price": 3.50, "category": "Grains"},
    {"name": "Milk", "quantity": 5, "price": 1.20, "category": "Dairy"},
    {"name": "Bread", "quantity": 3, "price": 0.80, "category": "Bakery"},
    {"name": "Tomatoes", "quantity": 8, "price": 0.45, "category": "Produce"},
]


def seed_items(clear_first=False):
    now = datetime.now(UTC)
    docs = [
        {
            **item,
            "added_at": now,
            "purchased": False,
        }
        for item in SAMPLE_ITEMS
    ]

    if clear_first:
        shopping_collection.delete_many({})

    result = shopping_collection.insert_many(docs)
    print(f"Seeded {len(result.inserted_ids)} items.")


def list_items(limit=20):
    docs = shopping_collection.find().sort("added_at", -1).limit(limit)
    print(f"Latest {limit} items:\n")
    for item in docs:
        name = item.get("name", "Unknown")
        qty = item.get("quantity", 0)
        price = float(item.get("price", 0.0))
        category = item.get("category", "General")
        purchased = "yes" if item.get("purchased") else "no"
        print(f"- {name:12} qty={qty:<3} price=${price:<5.2f} category={category:<10} purchased={purchased}")


def clear_items():
    result = shopping_collection.delete_many({})
    print(f"Removed {result.deleted_count} items.")


def main():
    parser = argparse.ArgumentParser(description="Shopping list data utility")
    parser.add_argument("action", choices=["seed", "list", "clear"], nargs="?", default="list")
    parser.add_argument("--reset", action="store_true", help="Clear existing documents before seeding")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of items to print when listing")
    args = parser.parse_args()

    if args.action == "seed":
        seed_items(clear_first=args.reset)
    elif args.action == "clear":
        clear_items()
    else:
        list_items(limit=max(args.limit, 1))


if __name__ == "__main__":
    try:
        main()
    finally:
        client.close()