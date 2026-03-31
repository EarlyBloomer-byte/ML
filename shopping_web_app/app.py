import os
from datetime import UTC, datetime
from flask import Flask, flash, redirect, render_template, request, url_for
from pymongo import DESCENDING, MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from bson.objectid import ObjectId
from bson.errors import InvalidId

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

# MongoDB connection
uri = os.environ.get("MONGO_URI")
if not uri:
    raise ValueError("MONGO_URI environment variable not set")

client = MongoClient(uri, serverSelectionTimeoutMS=5000)
db = client["shopping_app_db"]
collection = db["shopping_list"]


def parse_positive_int(raw_value, default=1):
    """Return a positive integer from user input, or default on invalid values."""
    try:
        parsed = int(raw_value)
        return parsed if parsed > 0 else default
    except (TypeError, ValueError):
        return default


def parse_price(raw_value):
    """Coerce price input to a non-negative float rounded to 2 decimals."""
    try:
        parsed = round(float(raw_value), 2)
        return parsed if parsed >= 0 else 0.0
    except (TypeError, ValueError):
        return 0.0

@app.route("/")
def index():
    items = list(collection.find().sort("added_at", DESCENDING))
    total_items = len(items)
    total_quantity = sum(parse_positive_int(item.get("quantity"), 0) for item in items)
    estimated_total = sum(
        parse_positive_int(item.get("quantity"), 0) * parse_price(item.get("price"))
        for item in items
    )

    return render_template(
        "index.html",
        items=items,
        total_items=total_items,
        total_quantity=total_quantity,
        estimated_total=estimated_total,
    )

@app.route("/add", methods=["POST"])
def add_item():
    name = (request.form.get("name") or "").strip()
    quantity = parse_positive_int(request.form.get("quantity"), 1)
    price = parse_price(request.form.get("price"))
    category = (request.form.get("category") or "General").strip() or "General"

    if not name:
        flash("Item name is required.", "error")
        return redirect(url_for("index"))

    try:
        collection.insert_one({
            "name": name,
            "quantity": quantity,
            "price": price,
            "category": category,
            "purchased": False,
            "added_at": datetime.now(UTC),
        })
        flash(f"Added {name} to your list.", "success")
    except PyMongoError:
        flash("Could not add item right now. Please try again.", "error")

    return redirect(url_for("index"))


@app.route("/toggle/<item_id>", methods=["POST"])
def toggle_item(item_id):
    try:
        object_id = ObjectId(item_id)
    except InvalidId:
        flash("Invalid item id.", "error")
        return redirect(url_for("index"))

    item = collection.find_one({"_id": object_id})
    if not item:
        flash("Item not found.", "error")
        return redirect(url_for("index"))

    collection.update_one(
        {"_id": object_id},
        {"$set": {"purchased": not bool(item.get("purchased", False))}},
    )
    return redirect(url_for("index"))

@app.route("/delete/<item_id>", methods=["POST"])
def delete_item(item_id):
    try:
        collection.delete_one({"_id": ObjectId(item_id)})
    except InvalidId:
        flash("Invalid item id.", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)