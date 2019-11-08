import collections
import json
import time

import requests
from bs4 import BeautifulSoup

from rdparserlib import cookies

RD_BASE_PARAMS = {"sort": "saleranking", "it": "product", "lpurl": "%2Fproducts", "callback": "callback", "mpp": "96"}
RD_API_ENDPOINT = "https://member.restaurantdepot.com/hawkproxy/"


def done(page_html):
    return not page_html.find(id="ctl00_SearchBody_NavigationTop_lnkNext")

def process_page(page_html):
    page_inventory = collections.defaultdict(list)
    for product_item in page_html.find_all(attrs={"class": "product-item"}):
        category_name = product_item.find(attrs={"class": "category-name"}).text
        product_name = product_item.find(attrs={"class": "custom-listing-info"}).find("ul").find_all("li")[0].text
        page_inventory[category_name].append(product_name)
    return page_inventory

def _extract_html_from_callback(response_text):
    start = response_text.index("(")
    end = response_text.rindex(")")
    response_json = json.loads(response_text[start + 1:end])
    return BeautifulSoup(response_json["html"], "lxml")

def send_request(pageno, cookiejar):
    params = RD_BASE_PARAMS.copy()
    params["pg"] = str(pageno)
    response = requests.get(RD_API_ENDPOINT, params=params, cookies=cookiejar)
    return _extract_html_from_callback(response.text)

def _update_inventory(current_inventory, new_inventory, inventory_filepath):
    inventory = collections.defaultdict(list)
    inventory.update(current_inventory)
    for category, items in new_inventory.items():
        inventory[category].extend(items)

    if inventory_filepath:
        with open(inventory_filepath, 'w') as rd_inventory_file:
            json.dump(inventory, rd_inventory_file)
    
    return inventory

def _clear_inventory(inventory_filepath):
    with open(inventory_filepath, 'w') as rd_inventory_file:
        json.dump({}, rd_inventory_file)

def _load_cookies():
    cookiejar = requests.cookies.RequestsCookieJar()
    cookiejar.update(cookies.retrieve())
    return cookiejar

def download(inventory_filepath):
    cookiejar = _load_cookies()

    if inventory_filepath:
        _clear_inventory(inventory_filepath)

    inventory = {}
    pageno = 1
    while True:
        page_html = send_request(pageno, cookiejar)
        page_inventory = process_page(page_html)
        inventory = _update_inventory(inventory, page_inventory, inventory_filepath)

        if done(page_html):
            break

        pageno += 1

        # Since this is an unofficial API, self-throttle to avoid pissing them off.
        time.sleep(5)

    return inventory