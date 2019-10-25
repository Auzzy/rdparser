import json
import os

from zope.testbrowser.browser import Browser


def retrieve():
    browser = Browser("https://member.restaurantdepot.com/customer/account/login")
    browser.getControl(name="login[username]").value = os.environ["RDPARSER_USERNAME"]
    browser.getControl(name="login[password]").value = os.environ["RDPARSER_PASSWORD"]
    browser.getControl("Sign In").click()
    return dict(browser.cookies.items())
