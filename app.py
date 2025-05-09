from flask import Flask, render_template, session
from ChannelScraper import ChannelScraper

app = Flask(__name__)
app.secret_key = "hello"

@app.route('/home/')
@app.route('/')
def playlist():
    session["url"] = "https://www.youtube.com/@lorenzopiccini5423"

    playlist_scraper = ChannelScraper(session["url"])

    if not playlist_scraper.is_valid_url():
        return "Invalid URL"

    return render_template("playlistSelector.html", playlists = playlist_scraper.get_playlists_dict())


if __name__ == '__main__':
    app.run()
