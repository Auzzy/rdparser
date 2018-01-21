import atexit
import itertools
import os
import re
import shlex
import shutil
import string
import subprocess
import tempfile
import time

from splinter import Browser

ITEM_ROW_XPATH = '//tr[@class="rgRow"|@class="rgAltRow"]//label[@class="description"]'
PHANTOMJS_URL = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"
OPEN_CLOSE_TAG_RE = re.compile(r"<(.*?)>.*?</\1>")
SINGLE_TAG_RE = re.compile("<.*?>")

CATEGORY_CHECKBOX_TABLE_ID = "cphMainContent_chkCategories"

def install_phantomjs(phantomjs_url=PHANTOMJS_URL):
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

def init_browser():
    browser = Browser("phantomjs")
    browser.driver.set_window_size(2000, 10000)
    return browser

def strip_html(text):
    text = OPEN_CLOSE_TAG_RE.sub("", text)
    text = SINGLE_TAG_RE.sub("", text)
    return text

def login(browser):
    url = "http://member.restaurantdepot.com/Public/Login.aspx?ReturnUrl=%2fMember%2fSearchResults.aspx"
    browser.visit(url)
    browser.find_by_id("cphMainContent_txtUserName").fill("arisia.org")
    browser.find_by_id("cphMainContent_txtPassword").fill("1990")
    browser.find_by_id("cphMainContent_btnSubmit").click()

def search(browser, search_text):
    search_box = browser.find_by_id("cphMainContent_txtSearch")[0]
    search_box.fill(search_text)
    browser.find_by_id("cphMainContent_btnSearch").click()

    if not browser.is_text_present("Showing results for: \"{0}\"".format(search_text), wait_time=5):
        showing_results_for = browser.find_by_id("cphMainContent_lblSearchTerm")[0].text.strip('"')
        raise Exception("Showing results for \"{0}\", not \"{1}\"".format(showing_results_for, search_text))

def load_items(browser):
    table = browser.find_by_id("ctl00_cphMainContent_resultsGrid_ctl00")[0]
    return [strip_html(element.html) for element in table.find_by_xpath(ITEM_ROW_XPATH)]

def search_and_load(browser, search_str):
    repeat_count = 0
    while True:
        try:
            search(browser, search_str)
            return load_items(browser)
        except Exception as exc:
            print("ERROR: {0}".format(exc))
            repeat_count += 1
            if repeat_count >= 3:
                print("Search isn't working. Reloading the page...")
                browser.reload()
                repeat_count = 0

def load_items_by_search(browser, search_str):
    raw_items = search_and_load(browser, search_str)
    items = set(raw_items)
    print("{0}: FOUND {1} ITEMS".format(search_str, len(raw_items)))

    if len(raw_items) >= 50:
        print("Found 50 or more items ({0}) for search string \"{1}\". Descending into substrings.".format(len(raw_items), search_str))
        for search_letter in string.ascii_lowercase:
            items |= load_items_by_search(browser, search_str + search_letter)

    return items

def load_category_checkboxes(browser):
    if not browser.is_element_present_by_id(CATEGORY_CHECKBOX_TABLE_ID, wait_time=10):
        raise Exception("Category checkbox table never loaded.")

    category_checkbox_table = browser.find_by_id(CATEGORY_CHECKBOX_TABLE_ID)[0]
    table_cells = category_checkbox_table.find_by_tag("td")
    return [(cell.text, cell.find_by_tag("input")[0]._element.get_property("id")) for cell in table_cells]
    '''
    category_checkboxes = []
    for cell in table_cells:
        category_checkboxes.append((cell.text, cell.find_by_tag("input")[0]._element.get_property("id")))
    # return [("Beverages & Mixers", "cphMainContent_chkCategories_0")]
    return category_checkboxes
    '''

def load_restaurant_depot_inventory(browser):
    items_by_category = {}
    for category_name, category_checkbox_id in load_category_checkboxes(browser):
        browser.find_by_id(category_checkbox_id).check()

        time.sleep(3)

        items = set()
        for search_letter in string.ascii_lowercase:
            items |= load_items_by_search(browser, search_letter)
        items_by_category[category_name] = items
    return items_by_category

def write_inventory(items_by_category):
    sorted_categories = {category: list(sorted(list(items))) for category, items in items_by_category}
    with open("inventory.json", 'w') as inventory_file:
        json.dump(inventory_file, sorted_categories)

if __name__ == "__main__":
    install_phantomjs()
    with init_browser() as browser:
        login(browser)
        items_by_category = load_restaurant_depot_inventory(browser)
        write_inventory(items_by_category)