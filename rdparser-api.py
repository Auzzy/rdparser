import atexit
import json
import os
import shlex
import shutil
import string
import subprocess
import tempfile
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from splinter import Browser

PHANTOMJS_URL = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"

SEARCH_URL = "http://member.restaurantdepot.com/Member/SearchResults.aspx"
BASE_SEARCH_PARAMS = {"reset": "y"}
PRODUCTS_TABLE_ID = "ctl00_cphMainContent_resultsGrid_ctl00"
PRODUCT_ROW_FILTER = {"name": "tr", "class_": ["rgRow", "rgAltRow"]}
PRODUCT_NAME_FILTER = {"name": "label", "class_": "description"}


def write_inventory(inventory):
    with open("inventory.json", 'w') as inventory_file:
        json.dump(inventory_file, inventory_file)

def _extract_product_names(response):
    response_html = BeautifulSoup(response.text, "lxml")
    items_table = response_html.find(id=PRODUCTS_TABLE_ID)
    items_rows = items_table.find_all(**PRODUCT_ROW_FILTER)
    return [item_row.find(**PRODUCT_NAME_FILTER).get_text() for item_row in items_rows]

def _search(search_term, session):
    response = session.get(SEARCH_URL, params=_get_search_params(search_term))
    if response.history:
        url_path = urlparse(response.url).path
        if url_path == "/Public/Error":
            print(response.history)
            print("An error occurred. Retrying...")
            return _search(search_term, session)
        elif url_path == "/Public/Login.aspx":
            print(response.history)
            session.cookies.update(get_cookies())
            return _search(search_term, session)
        else:
            raise Exception("Unexpectedly redirected away from the search results: {}".format(response.url))
    return response

def _get_search_params(search_term):
    search_params = {"term": search_term}
    search_params.update(BASE_SEARCH_PARAMS)
    return search_params

def _gather_items(search_term, session):
    response = _search(search_term, session)
    return _extract_product_names(response)

def _retrieve_category_inventory(session, category_id, search_base=""):
    inventory = set()
    for char in string.ascii_lowercase:
        search_term = search_base + char
        items = _gather_items(search_term, session)
        print("{0}: FOUND {1} ITEMS".format(search_term, len(items)))
        
        inventory.update(items)

        if len(items) >= 50:
            overflow_inventory = _retrieve_category_inventory(session, category_id, search_base + char)
            inventory.update(overflow_inventory)
    return inventory

def _get_category_mapping(session):
    response = session.get(SEARCH_URL)
    response_html = BeautifulSoup(response.text, "lxml")
    category_dropdown = response_html.find(id="category")
    category_dropdown_options = category_dropdown.find_all("option")
    return {option.get_text(): option["value"] for option in category_dropdown_options}

def retrieve_inventory(session):
    category_mapping = _get_category_mapping(session)
    # return {name: _retrieve_category_inventory(session, id) for name, id in category_mapping.items()}
    inventory_by_category = {}
    for name, id in category_mapping.items():
        print(name)
        inventory_by_category[name] = _retrieve_category_inventory(session, id)
    return inventory_by_category


def _install_phantomjs(phantomjs_url=PHANTOMJS_URL):
    filename = "phantomjs.tar.bz2"
    
    tempdir = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, tempdir)
    
    filepath = os.path.join(tempdir, filename)
    download_phantomjs_cmd = "wget {0} -O {1}".format(phantomjs_url, filepath)
    subprocess.call(shlex.split(download_phantomjs_cmd))

    untar_phantomjs_cmd = "tar -xjvf {0} -C {1}".format(filepath, tempdir)
    untar_output = subprocess.check_output(shlex.split(untar_phantomjs_cmd))
    phantomjs_dir = untar_output.splitlines()[0].decode('utf-8')

    os.environ["PATH"] += ":" + os.path.join(tempdir, phantomjs_dir, "bin")

def _init_browser():
    try:
        browser = Browser("phantomjs")
    except Exception as exc:
        if exc.msg == "'phantomjs' executable needs to be in PATH.":
            _install_phantomjs()
            browser = Browser("phantomjs")
        else:
            raise
    browser.driver.set_window_size(2000, 10000)
    return browser

def _login(browser):
    url = "http://member.restaurantdepot.com/Public/Login.aspx?ReturnUrl=%2fMember%2fSearchResults.aspx"
    browser.visit(url)

    if not browser.is_element_present_by_id("cphMainContent_txtUserName", wait_time=10):
        raise Exception("Could not log in.")

    browser.find_by_id("cphMainContent_txtUserName").fill("arisia.org")
    browser.find_by_id("cphMainContent_txtPassword").fill("1990")
    browser.find_by_id("cphMainContent_btnSubmit").click()

def get_cookies():
    with _init_browser() as browser:
        _login(browser)
        time.sleep(5)
        return browser.cookies.all()

if __name__ == "__main__":
    session = requests.Session()
    session.cookies.update(get_cookies())
    start = time.time()
    try:
        inventory = retrieve_inventory(session)
    finally:
        print(time.time() - start)
    write_inventory(inventory)