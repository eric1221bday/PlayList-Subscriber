import pprint
import warnings
import json
from pathlib import Path
from datetime import datetime

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

    def access_playlist(self, id: str):
        response = self.youtube.playlistItems().list(
            part="contentDetails,snippet",
            maxResults=50,
            playlistId=id
        ).execute()

        self.playlists[id]["length"] = int(response["pageInfo"]["totalResults"])
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
        times = [datetime.strptime(video["contentDetails"]["videoPublishedAt"], '%Y-%m-%dT%H:%M:%S.000Z')
                 for video in videos
                 if "videoPublishedAt" in video["contentDetails"]]
        self.playlists[id]["most_recent"] = max(times).isoformat()
        return videos

    def add_playlist(self, id: str):
        if id not in self.playlists:
            self.playlists[id] = {}
            self.playlists[id]["unwatched"] = []
        else:
            warnings.warn("playlist already in system!")
            return
        self.access_playlist(id)
        # pprint.pprint(max(times).isoformat())

    def check_new(self):
        for key, value in self.playlists.items():
            videos = self.access_playlist(key)

