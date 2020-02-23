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

def get_price(product_item):
    price = None
    price_section = product_item.find("span", attrs={"class": "select-price"})
    if price_section:
        price = price_section.get_text(strip=True)
    else:
        price_section = product_item.find("select", attrs={"class": "product-package-select"})
        if price_section:
            price_element = price_section.find("option", value=lambda value: value, string=lambda text: text.strip().startswith("Unit"))
            if price_element:
                price = price_element.get_text(strip=True)[4:].strip()

    price = price.replace("$", "") if price else None
    return {
        "max": price,
        "min": price
    }

def process_page(page_html):
    page_inventory = []
    for product_item in page_html.find_all(attrs={"class": "product-item"}):
        category_name = product_item.find(attrs={"class": "category-name"}).get_text()
        product_name = product_item.find(attrs={"class": "custom-listing-info"}).find("ul").find_all("li")[0].get_text()
        price = get_price(product_item)

        page_inventory.append({
            "name": product_name,
            "categories": [[category_name]],
            "price": price
        })

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
    current_inventory["inventory"].extend(new_inventory)
    
    if inventory_filepath:
        with open(inventory_filepath, 'w') as rd_inventory_file:
            json.dump(current_inventory, rd_inventory_file)
    
    return current_inventory

def _clear_inventory(inventory_filepath):
    inventory = {"inventory": []}
    with open(inventory_filepath, 'w') as rd_inventory_file:
        json.dump(inventory, rd_inventory_file)
    return inventory

def _load_cookies():
    cookiejar = requests.cookies.RequestsCookieJar()
    cookiejar.update(cookies.retrieve())
    return cookiejar

def download(inventory_filepath):
    cookiejar = _load_cookies()

    inventory = {}
    if inventory_filepath:
        inventory = _clear_inventory(inventory_filepath)

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