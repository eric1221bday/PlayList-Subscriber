import sys
import os
import warnings
import json
from pathlib import Path
import deps.rumps.rumps as rumps
from deps.rumps.rumps.rumps import Response
import dateutil.parser
import webbrowser
rumps.debug_mode(True)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class PlayListManager(rumps.App):
    playlists: dict
    youtube = None
    p = Path("playlists.json")
    playlist_window: rumps.Window
    TEMPLATE_PLAYLIST_URL = "https://www.youtube.com/playlist?list="
    TEMPLATE_URL = "https://www.youtube.com/watch?v=%s"
    switch: bool

    def __init__(self, youtube):
        if self.p.exists():
            with open("playlists.json", "r") as fp:
                self.playlists = json.load(fp)
        else:
            self.playlists = {}
        super(PlayListManager, self).__init__("Playlists")
        self.menu = [
            "Preferences",
            rumps.MenuItem("Refresh", callback=self.refresh),
            "Add Playlist",
            rumps.separator,
            "Playlists",
            rumps.separator,
            "Quit"
        ]
        self.icon = resource_path("youtube.png")
        self.quit_button = None
        self.youtube = youtube
        self.playlist_window = rumps.Window(title="Add Playlist",
                                            default_text="Playlist URL",
                                            cancel=True,
                                            dimensions=(350, 20))
        self.check_new()
        self.switch = True
        for key, value in self.playlists.items():
            self.menu.insert_after("Playlists", value["title"])
            self.menu[value["title"]].add(rumps.MenuItem("Unsubscribe",
                                                         callback=self.unsubscribe, name=key))
            self.populate_playlist(self.menu[value["title"]], key)

    def populate_playlist(self, menu: rumps.MenuItem, playlist_id: str):
        for video_id, video_info in self.playlists[playlist_id]["unwatched"].items():
            if video_info["title"] not in menu:
                menu.add(rumps.MenuItem(video_info["title"],
                                        callback=self.video_clicked,
                                        name=playlist_id + "/" + video_id))
        for key in menu.keys():
            if key == "Unsubscribe": continue
            video_id = menu[key].name.split("/")[1]
            if video_id not in self.playlists[playlist_id]["unwatched"]:
                del menu[key]

    def access_playlist(self, serial: str):
        playlist_items_info = self.youtube.playlistItems().list(
            part="contentDetails,snippet",
            maxResults=50,
            playlistId=serial
        ).execute()
        # pprint.pprint(playlist_items_info)
        playlist_info = self.youtube.playlists().list(
            part="snippet",
            id=serial
        ).execute()

        # pprint.pprint(playlist_info["items"][0]["snippet"]["title"])
        self.playlists[serial]["title"] = playlist_info["items"][0]["snippet"]["title"]

        self.playlists[serial]["length"] = int(playlist_items_info["pageInfo"]["totalResults"])
        self.playlists[serial]["videos"]: list = playlist_items_info["items"]

        if "nextPageToken" in playlist_items_info:
            while "nextPageToken" in playlist_items_info:
                playlist_items_info = self.youtube.playlistItems().list(
                    part="contentDetails,snippet",
                    maxResults=50,
                    playlistId=serial,
                    pageToken=playlist_items_info["nextPageToken"]
                ).execute()
                self.playlists[serial]["videos"].extend(playlist_items_info["items"])

        times = [dateutil.parser.parse(video["contentDetails"]["videoPublishedAt"])
                 for video in self.playlists[serial]["videos"]
                 if "videoPublishedAt" in video["contentDetails"]]
        # print([time.isoformat() for time in times])
        self.playlists[serial]["most_recent"] = max(times).isoformat()

    def add_playlist(self, serial: str):
        if serial not in self.playlists:
            self.playlists[serial] = {}
            self.playlists[serial]["unwatched"] = {}
        else:
            warnings.warn("playlist already in system!")
            return
        try:
            self.access_playlist(serial)
            return True
        except:
            self.playlists.pop(serial, None)
            return False
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
                        videoId = video["contentDetails"]["videoId"]
                        if videoId not in self.playlists[key]["unwatched"]:
                            self.playlists[key]["unwatched"][videoId] = {
                                    "title": video["snippet"]["title"],
                                    "position": video["snippet"]["position"],
                                }
                    else:
                        return

    @rumps.clicked("Preferences")
    def prefs(self, _):
        rumps.Window("I can't think of a good example app...").run()

    @rumps.clicked("Add Playlist")
    def add_playlist_clicked(self, _):
        response: Response = self.playlist_window.run()
        if response.clicked:
            if self.TEMPLATE_PLAYLIST_URL not in response.text:
                warnings.warn("Not a valid playlist URL!")
                return
            serial = response.text.replace(self.TEMPLATE_PLAYLIST_URL, "")
            if self.add_playlist(serial):
                self.menu.insert_after("Playlists", self.playlists[serial]["title"])
            else:
                warnings.warn("Adding Playlist Failed")

    def unsubscribe(self, sender):
        print(sender.name)
        print(sender.title)
        print("Afraid of memory leaks")

    @rumps.clicked("Quit")
    def exit_save(self, _):
        playlists_save = {}
        for key, value in self.playlists.items():
            playlists_save[key] = {"unwatched": value["unwatched"], "most_recent": value["most_recent"]}
        with open("playlists.json", "w") as fp:
            json.dump(playlists_save, fp)
        fp.close()
        rumps.quit_application()

    @rumps.timer(1800)
    def refresh(self, _):
        self.check_new()
        for key, value in self.playlists.items():
            self.populate_playlist(self.menu[value["title"]], key)

    def video_clicked(self, sender: rumps.MenuItem):
        two = sender.name.split("/")
        webbrowser.open(self.TEMPLATE_URL % two[1])
        self.playlists[two[0]]["unwatched"].pop(two[1])
        return

    # @rumps.clicked("Memory Test")
    # def update_menu(self, _):
    #     if self.switch:
    #         for i in range(1000):
    #             self.menu.add(str(i))
    #     else:
    #         for i in range(1000):
    #             del self.menu[str(i)]
    #     self.switch = not self.switch
