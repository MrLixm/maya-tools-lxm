"""

!! This module can't import any other package module !!

This file has to be place at the root of the module:
    ex: /ModuleName/constants.py
"""
import json
import os

MODULE_PATH = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(MODULE_PATH, "resources")
VENDOR_DIR = os.path.join(MODULE_PATH, "vendor")

# initiliazed empty
APPNAME = None
VERSION = None


def read_appinfo():
    global APPNAME
    global VERSION

    app_json_path = os.path.join(MODULE_PATH, "appinfo.json")
    with open(app_json_path, "r") as app_file:
        app_data = json.load(app_file)

    APPNAME = app_data.get("NAME")
    VERSION = app_data.get("VERSION")

    return


read_appinfo()

# used when registering the interface
APPNAME_UI = "{}".format(APPNAME)
