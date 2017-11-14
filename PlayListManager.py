import pprint
import warnings
import json
from pathlib import Path
from datetime import datetime
import dateutil.parser

class PlayListManager:
    playlists: dict
    youtube = None
    p = Path("playlists.json")

    def __init__(self, youtube):
        self.youtube = youtube
        if self.p.exists():
            with open("playlists.json", "r") as fp:
                self.playlists = json.load(fp)
        else:
            self.playlists = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open("playlists.json", "w") as fp:
            json.dump(self.playlists, fp)
        fp.close()
        return

    def access_playlist(self, serial: str):
        response = self.youtube.playlistItems().list(
            part="contentDetails,snippet",
            maxResults=50,
            playlistId=serial
        ).execute()

        self.playlists[serial]["length"] = int(response["pageInfo"]["totalResults"])
        videos: list = response["items"]

        if "nextPageToken" in response:
            while "nextPageToken" in response:
                response = self.youtube.playlistItems().list(
                    part="contentDetails,snippet",
                    maxResults=50,
                    playlistId="PLVmM0UVcquYI-O-SKrE4n4FZBrzBV-Ir7",
                    pageToken=response["nextPageToken"]
                ).execute()
                videos.extend(response["items"])

        times = [dateutil.parser.parse(video["contentDetails"]["videoPublishedAt"])
                 for video in videos
                 if "videoPublishedAt" in video["contentDetails"]]
        print(max(times).astimezone())
        self.playlists[serial]["most_recent"] = max(times).isoformat()
        return videos

    def add_playlist(self, serial: str):
        if serial not in self.playlists:
            self.playlists[serial] = {}
            self.playlists[serial]["unwatched"] = []
        else:
            warnings.warn("playlist already in system!")
            return
        self.access_playlist(serial)
        # pprint.pprint(max(times).isoformat())

    def check_new(self):
        for key, value in self.playlists.items():
            old_recent = dateutil.parser.parse(self.playlists[key]["most_recent"])
            # pprint.pprint(old_recent)
            videos = self.access_playlist(key)

