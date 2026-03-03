import os
from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)

# MongoDB connection
uri = os.environ.get("MONGO_URI")
client = MongoClient(uri)
db = client["shopping_app_db"]
collection = db["shopping_list"]

@app.route("/")
def index():
    items = list(collection.find())
    return render_template("index.html", items=items)

@app.route("/add", methods=["POST"])
def add_item():
    name = request.form.get("name")
    quantity = request.form.get("quantity")

    if name and quantity:
        collection.insert_one({
            "name": name,
            "quantity": int(quantity)
        })

    return redirect("/")

@app.route("/delete/<item_id>")
def delete_item(item_id):
    collection.delete_one({"_id": ObjectId(item_id)})
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)