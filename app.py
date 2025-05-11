import time
from multiprocessing.pool import ThreadPool

from flask import Flask, render_template, session, request, send_file
import pytubefix
import os
import zipfile
import tempfile

from ChannelScraper import ChannelScraper

app = Flask(__name__)
app.secret_key = "hello"

@app.route('/home/', methods = ["POST", "GET"])
@app.route('/', methods = ["POST", "GET"])

def playlist():
    if request.method == "POST":
        selected_playlist = pytubefix.Playlist(request.form["selected_playlist"]).videos

        with tempfile.TemporaryDirectory(prefix="download", ignore_cleanup_errors=True) as download_folder:

            with ThreadPool(processes=8) as pool:
                pool.map_async(download, ((video, download_folder) for video in selected_playlist)).get()

            with zipfile.ZipFile(download_folder + "\\file.zip", "w") as f:
                for file in os.listdir(download_folder + "\\playlist"):
                    song = download_folder + "\\playlist\\" + file
                    f.write(song, "Playlist\\" + file.title())

            return send_file(download_folder + "\\file.zip", as_attachment=True)

    session["url"] = "https://www.youtube.com/@lorenzopiccini5423"

    playlist_scraper = ChannelScraper(session["url"])

    if not playlist_scraper.is_valid_url():
        return "Invalid URL"

    session["playlist_dict"] = playlist_scraper.get_playlists_dict()

    return render_template("playlistSelector.html", playlists = playlist_scraper.get_playlists_dict())

def download(info):
    video: pytubefix.__main__.YouTube = info[0]
    download_folder = info[1]

    video.streams.get_audio_only().download(download_folder + "\\playlist")

if __name__ == '__main__':
    app.run()
