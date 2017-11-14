import json
import os
import pprint
import json
import argparse
from PlayListManager import PlayListManager

from googleapiclient.discovery import build

DEVELOPER_KEY = "YOUR KEY"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Options for the playlist subscriber")
    parser.add_argument("key", type=str)
    args = parser.parse_args()
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=args.key)
    with PlayListManager(youtube) as manager:
        manager.add_playlist("PLVmM0UVcquYI-O-SKrE4n4FZBrzBV-Ir7")
        manager.check_new()
