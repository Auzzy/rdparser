import atexit
import os
import shlex
import shutil
import subprocess
import tempfile
import time

from splinter import Browser


PHANTOMJS_URL = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"

def _install_phantomjs(phantomjs_url=PHANTOMJS_URL):
    filename = "phantomjs.tar.bz2"

    tempdir = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, tempdir)

    filepath = os.path.join(tempdir, filename)
    download_phantomjs_cmd = "wget {0} -O {1}".format(phantomjs_url, filepath)
    subprocess.call(shlex.split(download_phantomjs_cmd), stderr=subprocess.DEVNULL)

    untar_phantomjs_cmd = "tar -xjvf {0} -C {1}".format(filepath, tempdir)
    untar_output = subprocess.check_output(shlex.split(untar_phantomjs_cmd), stderr=subprocess.DEVNULL)
    phantomjs_dir = untar_output.splitlines()[0].decode('utf-8')

    os.environ["PATH"] += ":" + os.path.join(tempdir, phantomjs_dir, "bin")

def _init_browser():
    try:
        browser = Browser("phantomjs")
    except Exception as exc:
        if exc.msg.strip() == "'phantomjs' executable needs to be in PATH.":
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

def retrieve():
    with _init_browser() as browser:
        _login(browser)
        time.sleep(5)
        return browser.cookies.all()
