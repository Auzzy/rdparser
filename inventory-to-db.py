import collections
import json
import os
import sqlite3
import sys

INVENTORY_DIR = "/home/auzzy/git/rdparser/inventory/"

def load_inventory():
    category_to_products = {}
    for category_filename in os.listdir(INVENTORY_DIR):
        category_name = os.path.splitext(category_filename)[0].replace("-", " ")
        with open(os.path.join(INVENTORY_DIR, category_filename)) as category_file:
            category_to_products[category_name] = [product.strip() for product in set(json.load(category_file))]

    return category_to_products

inventory = load_inventory()

db_path = sys.argv[1] if len(sys.argv) >= 1 else "inventory.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("PRAGMA foreign_keys = ON")
cursor.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, store TEXT, parentid INTEGER, FOREIGN KEY(parentid) REFERENCES categories(id))")
cursor.execute("""CREATE TABLE IF NOT EXISTS products (name, categoryid, url, store, stocked)""")

store = "Restaurant Depot"
# cursor.execute("INSERT INTO categories (name, store) VALUES (?, ?)", (store, store))
# root_category_id = cursor.lastrowid
root_category_id = None
for category, products in inventory.items():
    # cursor.execute("INSERT INTO categories (name, store, parentid) VALUES (?, ?, ?)", (category, store, root_category_id))
    cursor.execute("INSERT INTO categories (name, store, parentid) VALUES (?, ?, ?)", (category, store, root_category_id))
    category_id = cursor.lastrowid
    for product in products:
        cursor.execute("INSERT INTO products (name, categoryid, url, store, stocked) VALUES (?, ?, ?, ?, ?)", (product, category_id, None, store, None))


connection.commit()
connection.close()
