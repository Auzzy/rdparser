import argparse
import collections
import json
import os
import sqlite3

def _load_inventory(inventory_filepath):
    with open(inventory_filepath) as inventory_file:
        return json.load(inventory_file)

def _db_disconnect(cursor, connection):
    connection.commit()
    connection.close()

def _insert_inventory(cursor, inventory):
    store = "Restaurant Depot"
    for category, products in inventory.items():
        cursor.execute("INSERT INTO categories (name, store) VALUES (?, ?)", (category, store))
        category_id = cursor.lastrowid
        for product in products:
            cursor.execute("INSERT INTO products (name, categoryid, url, store, stocked) VALUES (?, ?, ?, ?, ?)", (product, category_id, None, store, None))

def _create_tables(cursor):
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, store TEXT, parentid INTEGER, FOREIGN KEY(parentid) REFERENCES categories(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS products (name, categoryid, url, store, stocked)")

def _db_connect(database_filepath):
    connection = sqlite3.connect(database_filepath)
    cursor = connection.cursor()
    return connection, cursor

def populate(inventory, database_filepath):
    connection, cursor = _db_connect(database_filepath)

    _create_tables(cursor)
    _insert_inventory(cursor, inventory)

    _db_disconnect(cursor, connection)

def populate_from_file(inventory_filepath, database_filepath):
    populate(_load_inventory(inventory_filepath), database_filepath)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("database_filepath")
    parser.add_argument("inventory_filepath")
    return vars(parser.parse_args())

if __name__ == "__main__":
    args = parse_args()
    populate_from_file(args["inventory_filepath"], args["database_filepath"])