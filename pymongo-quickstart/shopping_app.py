import os
from pymongo import MongoClient
from datetime import datetime, UTC

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

# Sample shopping items
items = [
    {"name": "Rice", "quantity": 2, "price": 3500, "added_at": datetime.now(UTC)},
    {"name": "Milk", "quantity": 5, "price": 1200, "added_at": datetime.now(UTC)},
    {"name": "Bread", "quantity": 3, "price": 800, "added_at": datetime.now(UTC)},
]

# Insert items into collection
shopping_collection.insert_many(items)

print("Items added successfully!\n")

# Retrieve and display items
for item in shopping_collection.find():
    print(item)

client.close()