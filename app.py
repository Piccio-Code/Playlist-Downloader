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
            for video in selected_playlist:
                ys = video.streams.get_audio_only()
                ys.download(download_folder + "\\playlist")

            print(os.listdir(download_folder + "\\playlist"))
            with zipfile.ZipFile(download_folder + "\\file.zip", "w") as f:
                for file in os.listdir(download_folder + "\\playlist"):
                    song = download_folder + "\\playlist\\" + file
                    f.write(song, "\\Playlist" + file.title())

            return send_file(download_folder + "\\file.zip", as_attachment=True)

    session["url"] = "https://www.youtube.com/@lorenzopiccini5423"

    playlist_scraper = ChannelScraper(session["url"])

    if not playlist_scraper.is_valid_url():
        return "Invalid URL"

    session["playlist_dict"] = playlist_scraper.get_playlists_dict()

    return render_template("playlistSelector.html", playlists = playlist_scraper.get_playlists_dict())


if __name__ == '__main__':
    app.run()
