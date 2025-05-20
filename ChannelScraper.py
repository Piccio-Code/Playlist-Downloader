from multiprocessing.pool import ThreadPool

from pytubefix import Channel
import requests


class ChannelScraper:
    def __init__(self, channel_url: str):
        self.channel_url = channel_url
        self.channel: Channel = None

    def is_valid_url(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        is_valid = requests.get(self.channel_url, headers=headers).status_code == 200 and "youtube.com" in self.channel_url

        if is_valid:
            self.channel = Channel(self.channel_url)

        return is_valid


    def get_playlists_dict(self):
        playlists = self.channel.playlists

        with ThreadPool(processes=len(playlists)) as pool:
            result = pool.map(lambda playlist: {"title": playlist.title, "url": playlist.playlist_url, "thumbnail_url": playlist.thumbnail_url}, playlists)
            return result