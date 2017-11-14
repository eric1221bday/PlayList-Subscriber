import json
import os
import pprint
import json
from PlayListManager import PlayListManager

from googleapiclient.discovery import build

DEVELOPER_KEY = "AIzaSyAzdmVlblOrpZm7pWMK63fcy-_J96haOYw"
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

if __name__ == '__main__':
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=DEVELOPER_KEY)
    manager = PlayListManager(youtube)
    manager.add_playlist("PLVmM0UVcquYI-O-SKrE4n4FZBrzBV-Ir7")

