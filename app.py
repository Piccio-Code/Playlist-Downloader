import shutil
import time
from multiprocessing.pool import ThreadPool

from click.shell_completion import ShellCompleteType
from flask import Flask, render_template, session, request, send_file, redirect, url_for, jsonify
import pytubefix
import os
import zipfile
import tempfile
from ChannelScraper import ChannelScraper

app = Flask(__name__, static_url_path='/static')
app.secret_key = "hello"

@app.route("/home/")
@app.route('/')
def channel_selector():
    return render_template("mainPage.html", url = url_for("playlist"))

@app.route('/playlist_selector/')
def playlist():
    playlist_scraper = ChannelScraper(session["url"])
    playlist_scraper.is_valid_url()

    session["playlist_dict"] = playlist_scraper.get_playlists_dict()

    return render_template("playlistSelector.html", playlists=playlist_scraper.get_playlists_dict(), url_main_page=url_for("channel_selector"))

@app.route("/get_files/", methods=["POST"])
def get_files():
    if request.is_json:
        session["selected_playlist"] = request.json.get("url")
        selected_playlist = pytubefix.Playlist(session["selected_playlist"])
        download_folder = tempfile.mkdtemp(prefix="download")

        # Create the playlist folder
        playlist_folder = os.path.join(download_folder, "playlist")
        os.makedirs(playlist_folder, exist_ok=True)

        with ThreadPool(processes=8) as pool:
            pool.map(download, ((video, download_folder) for video in selected_playlist))

        zip_path = os.path.join(download_folder, "playlist.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in os.listdir(playlist_folder):
                song_path = os.path.join(playlist_folder, file)
                zipf.write(song_path, os.path.join("playlist", file))

        try:
            return send_file(zip_path, as_attachment=True)
        finally:
            shutil.rmtree(download_folder, ignore_errors=True)

@app.route("/send_url/", methods = ["POST"])
def send_url():
    url = request.json.get("url")

    if "https://" not in url:
        return {"isFailed": True}

    playlist_scraper = ChannelScraper(url)

    if not playlist_scraper.is_valid_url():
        return {"isFailed": True}

    session["url"] = url
    return {"isFailed": False}


def download(info):
    video = pytubefix.__main__.YouTube(info[0])
    download_folder = info[1]
    video.streams.get_audio_only().download(os.path.join(download_folder, "playlist"))


if __name__ == '__main__':
    app.run()