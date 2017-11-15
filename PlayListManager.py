import pprint
import warnings
import json
from pathlib import Path
import rumps
import dateutil.parser


class PlayListManager(rumps.App):
    playlists: dict
    youtube = None
    p = Path("playlists.json")

    def __init__(self, youtube):
        super(PlayListManager, self).__init__("Playlists")
        self.menu = ["Preferences", "add_thing"]
        self.youtube = youtube
        if self.p.exists():
            with open("playlists.json", "r") as fp:
                self.playlists = json.load(fp)
        else:
            self.playlists = {}

    def __enter__(self):
        self.check_new()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        playlists_save = {}
        for key, value in self.playlists.items():
            playlists_save[key] = {"unwatched": value["unwatched"], "most_recent": value["most_recent"]}
        with open("playlists.json", "w") as fp:
            json.dump(playlists_save, fp)
        fp.close()
        return

    def access_playlist(self, serial: str):
        playlist_items_info = self.youtube.playlistItems().list(
            part="contentDetails,snippet",
            maxResults=50,
            playlistId=serial
        ).execute()

        playlist_info = self.youtube.playlists().list(
            part="snippet",
            id=serial
        ).execute()

        pprint.pprint(playlist_info["items"][0]["snippet"]["title"])
        self.playlists[serial]["title"] = playlist_info["items"][0]["snippet"]["title"]

        self.playlists[serial]["length"] = int(playlist_items_info["pageInfo"]["totalResults"])
        self.playlists[serial]["videos"]: list = playlist_items_info["items"]

        if "nextPageToken" in playlist_items_info:
            while "nextPageToken" in playlist_items_info:
                playlist_items_info = self.youtube.playlistItems().list(
                    part="contentDetails,snippet",
                    maxResults=50,
                    playlistId="PLVmM0UVcquYI-O-SKrE4n4FZBrzBV-Ir7",
                    pageToken=playlist_items_info["nextPageToken"]
                ).execute()
                self.playlists[serial]["videos"].extend(playlist_items_info["items"])

        times = [dateutil.parser.parse(video["contentDetails"]["videoPublishedAt"])
                 for video in self.playlists[serial]["videos"]
                 if "videoPublishedAt" in video["contentDetails"]]
        print(max(times).isoformat())
        self.playlists[serial]["most_recent"] = max(times).isoformat()

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
            self.access_playlist(key)
            for video in reversed(self.playlists[key]["videos"]):
                if "videoPublishedAt" in video["contentDetails"]:
                    time_published = dateutil.parser.parse(video["contentDetails"]["videoPublishedAt"])
                    if time_published > old_recent:
                        self.playlists[key]["unwatched"].append(video)
                    else:
                        return

    @rumps.clicked("Preferences")
    def prefs(self, _):
        rumps.Window("I can't think of a good example app...").run()

    @rumps.clicked("add_thing")
    def add_thing(self, _):
        self.menu.add("added")
