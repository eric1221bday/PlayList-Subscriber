import pprint
import os
from pathlib import Path


class PlayListManager:
    playlists: dict
    youtube = None

    def __init__(self, youtube):
        p = Path('playlists.json')
        self.youtube = youtube
        if p.exists():
            self.playlists = None
        else:
            self.playlists = {}

    def add_playlist(self, id: str):
        self.playlists[id] = {}
        response = self.youtube.playlistItems().list(
            part='contentDetails',
            maxResults=50,
            playlistId=id
        ).execute()

        self.playlists[id]['length'] = int(response['pageInfo']['totalResults'])
        self.playlists[id]['videos'] = response['items']

        if 'nextPageToken' in response:
            while 'nextPageToken' in response:
                response = self.youtube.playlistItems().list(
                    part='contentDetails',
                    maxResults=50,
                    playlistId="PLVmM0UVcquYI-O-SKrE4n4FZBrzBV-Ir7",
                    pageToken=response['nextPageToken']
                ).execute()
                self.playlists[id]['videos'].append(response['items'])
        pprint.pprint(self.playlists[id])
