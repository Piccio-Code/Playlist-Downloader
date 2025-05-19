from multiprocessing.pool import ThreadPool

from pytubefix import Channel
import requests


class ChannelScraper:
    def __init__(self, channel_url: str):
        self.channel_url = channel_url
        self.channel: Channel = None

    def is_valid_url(self):
        is_valid = requests.get(self.channel_url).status_code == 200 and "https://www.youtube.com/@" in self.channel_url

        if is_valid:
            self.channel = Channel(self.channel_url)

        return is_valid


    def get_playlists_dict(self):
        playlists = self.channel.playlists

        with ThreadPool(processes=len(playlists)) as pool:
            result = pool.map(lambda playlist: {"title": playlist.title, "url": playlist.playlist_url, "thumbnail_url": playlist.thumbnail_url}, playlists)
            return result