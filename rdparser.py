import json
import multiprocessing
import string
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

import cookies


SEARCH_URL = "http://member.restaurantdepot.com/Member/SearchResults.aspx"
BASE_SEARCH_PARAMS = {"reset": "y"}
PRODUCTS_TABLE_ID = "ctl00_cphMainContent_resultsGrid_ctl00"
PRODUCT_ROW_FILTER = {"name": "tr", "class_": ["rgRow", "rgAltRow"]}
PRODUCT_NAME_FILTER = {"name": "label", "class_": "description"}


def write_inventory(inventory):
    with open("inventory.json", 'w') as inventory_file:
        json.dump(inventory, inventory_file)

def _extract_product_names(response):
    response_html = BeautifulSoup(response.text, "lxml")
    items_table = response_html.find(id=PRODUCTS_TABLE_ID)
    items_rows = items_table.find_all(**PRODUCT_ROW_FILTER)
    return [item_row.find(**PRODUCT_NAME_FILTER).get_text() for item_row in items_rows]

def _retry_get(session, url, retries=4, timeout=10, **kwargs):
    try_count = 0
    current_timeout = timeout
    while try_count < retries + 1:
        try_count += 1
        try:
            return session.get(url, timeout=current_timeout, **kwargs)
        except requests.exceptions.Timeout as exc:
            query_str = "&".join(["{}={}".format(key, value) for key, value in kwargs.get("params").items()])
            print("Timeout: {}?{}".format(url, query_str))
            current_timeout *= 2
    else:
        raise Exception("Retrying the request fatally failed.")

def _search(search_term, category_id, session):
    try:
        response = _retry_get(session, SEARCH_URL, params=_get_search_params(search_term, category_id))
    except Exception:
        # Try refreshing the cookies, and if it fails again, let the Exception be raised
        session.cookies.update(cookies.retrieve())
        response = _retry_get(session, SEARCH_URL, params=_get_search_params(search_term))

    if response.history:
        url_path = urlparse(response.url).path
        if url_path == "/Public/Error.aspx":
            print(response.history)
            print("An error occurred. Retrying...")
            return _search(search_term, category_id, session)
        elif url_path == "/Public/Login.aspx":
            print(response.history)
            session.cookies.update(cookies.retrieve())
            return _search(search_term, category_id, session)
        else:
            raise Exception("Unexpectedly redirected away from the search results: {}".format(response.url))
    return response

def _get_search_params(search_term, category_id):
    search_params = {"term": search_term, "category": category_id}
    search_params.update(BASE_SEARCH_PARAMS)
    return search_params

def _gather_items(search_term, category_id, session):
    response = _search(search_term, category_id, session)
    return _extract_product_names(response)

def _walk_category_inventory(session, category_id, category_name, search_base=""):
    inventory = set()
    for char in string.ascii_lowercase:
        search_term = search_base + char
        items = _gather_items(search_term, category_id, session)
        print("[{}] {}: FOUND {} ITEMS".format(category_name, search_term, len(items)))
        
        inventory.update(items)

        if len(items) >= 50:
            overflow_inventory = _walk_category_inventory(session, category_id, category_name, search_base + char)
            inventory.update(overflow_inventory)
    return list(inventory)

def _retrieve_category_inventory(category_id, category_name):
    with requests.Session() as session:
        session.cookies.update(cookies.retrieve())
        return _walk_category_inventory(session, category_id, category_name)

def _get_category_mapping():
    response = requests.get(SEARCH_URL, cookies=cookies.retrieve())
    response_html = BeautifulSoup(response.text, "lxml")
    category_dropdown = response_html.find(id="category")
    category_dropdown_options = category_dropdown.find_all("option")
    return {option.get_text(): option["value"] for option in category_dropdown_options if option.get_text().strip().lower() != "department"}

def retrieve_inventory():
    category_mapping = _get_category_mapping()
    inventory_by_category = {}
    with multiprocessing.Pool() as pool:
        promises = {}
        for name, id in category_mapping.items():
            promises[name] = pool.apply_async(_retrieve_category_inventory, (id, name))

        for category, promise in promises.items():
            inventory_by_category[category] = promise.get()
    return inventory_by_category

if __name__ == "__main__":
    start = time.time()
    try:
        inventory = retrieve_inventory()
    finally:
        print(time.time() - start)
    write_inventory(inventory)
