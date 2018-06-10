import collections
import json
import os
import sqlite3
import sys

INVENTORY_FILEPATH = "/home/auzzy/git/rdparser/inventory.json"

def load_inventory():
    with open(INVENTORY_FILEPATH) as inventory_file:
        return json.load(inventory_file)

inventory = load_inventory()

db_path = sys.argv[1] if len(sys.argv) >= 1 else "inventory.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("PRAGMA foreign_keys = ON")
cursor.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, store TEXT, parentid INTEGER, FOREIGN KEY(parentid) REFERENCES categories(id))")
cursor.execute("""CREATE TABLE IF NOT EXISTS products (name, categoryid, url, store, stocked)""")

store = "Restaurant Depot"
for category, products in inventory.items():
    cursor.execute("INSERT INTO categories (name, store) VALUES (?, ?)", (category, store))
    category_id = cursor.lastrowid
    for product in products:
        cursor.execute("INSERT INTO products (name, categoryid, url, store, stocked) VALUES (?, ?, ?, ?, ?)", (product, category_id, None, store, None))


connection.commit()
connection.close()
