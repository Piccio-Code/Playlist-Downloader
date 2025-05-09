import os
import shutil
import zipfile
from flask import Flask, render_template, session, request, send_file
import pytubefix

from ChannelScraper import ChannelScraper

app = Flask(__name__)
app.secret_key = "hello"

@app.route('/home/', methods = ["POST", "GET"])
@app.route('/', methods = ["POST", "GET"])

def playlist():
    if request.method == "POST":
        selected_playlist = pytubefix.Playlist(request.form["selected_playlist"]).videos

        DOWNLOAD_FILE_NAME = "downloads/" + pytubefix.Playlist(request.form["selected_playlist"]).title + ".zip"
        TEMP_FILE_NAME = "downloads/playlist"

        for video in selected_playlist:
            ys = video.streams.get_audio_only()
            ys.download(TEMP_FILE_NAME)

        with zipfile.ZipFile(DOWNLOAD_FILE_NAME, "w") as f:
            for file in os.listdir(TEMP_FILE_NAME):
                f.write(TEMP_FILE_NAME + "/" + file)

        return send_file(DOWNLOAD_FILE_NAME, as_attachment=True)

    shutil.rmtree("downloads")

    session["url"] = "https://www.youtube.com/@lorenzopiccini5423"

    playlist_scraper = ChannelScraper(session["url"])

    if not playlist_scraper.is_valid_url():
        return "Invalid URL"

    session["playlist_dict"] = playlist_scraper.get_playlists_dict()

    return render_template("playlistSelector.html", playlists = playlist_scraper.get_playlists_dict())


if __name__ == '__main__':
    app.run()
