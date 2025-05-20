import shutil
import time
import random
import logging
from multiprocessing.pool import ThreadPool
from functools import partial
import requests
from urllib.parse import urlparse

from flask import Flask, render_template, session, request, send_file, redirect, url_for
import pytubefix
import os
import zipfile
import tempfile
from ChannelScraper import ChannelScraper
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)  # More secure random key

# List of common referrers to rotate through
REFERRERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.youtube.com/",
    "https://www.facebook.com/",
    "https://www.reddit.com/",
    "https://www.twitter.com/"
]

# Session timeouts
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour


class HumanizedDownloader:
    @staticmethod
    def get_random_user_agent():
        try:
            ua = UserAgent()
            return ua.random
        except Exception:
            # Fallback user agents in case the library fails
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
            ]
            return random.choice(user_agents)

    @staticmethod
    def add_human_delay():
        """Add a random delay to simulate human behavior"""
        delay = random.uniform(1.5, 4.2)
        time.sleep(delay)

    @staticmethod
    def get_random_referrer():
        """Get a random referrer"""
        return random.choice(REFERRERS)


@app.route("/home/")
@app.route('/')
def channel_selector():
    if "url" in session:
        return redirect(url_for("playlist"))

    return render_template("mainPage.html", url=url_for("playlist"))


@app.route('/playlist_selector/')
def playlist():
    if "url" not in session:
        return redirect(url_for("channel_selector"))

    try:
        # Add human-like delay
        HumanizedDownloader.add_human_delay()

        playlist_scraper = ChannelScraper(session["url"])
        if not playlist_scraper.is_valid_url():
            # Invalid URL, redirect back to channel selector
            session.pop("url", None)
            return redirect(url_for("channel_selector"))

        session["playlist_dict"] = playlist_scraper.get_playlists_dict()

        return render_template("playlistSelector.html",
                               playlists=playlist_scraper.get_playlists_dict(),
                               url_main_page=url_for("channel_selector"))

    except Exception as e:
        logger.error(f"Error in playlist route: {str(e)}")
        session.pop("url", None)
        return redirect(url_for("channel_selector"))


@app.route("/get_files/", methods=["POST"])
def get_files():
    try:
        if request.is_json:
            session["selected_playlist"] = request.json.get("url")
            selected_playlist = pytubefix.Playlist(session["selected_playlist"])
            download_folder = tempfile.mkdtemp(prefix="download")

            playlist_folder = os.path.join(download_folder, "playlist")
            os.makedirs(playlist_folder, exist_ok=True)

            # Get all video URLs with a human-like delay
            HumanizedDownloader.add_human_delay()
            video_urls = selected_playlist.video_urls

            # Shuffle the videos to make the download pattern less predictable
            random.shuffle(video_urls)

            # Use a partial function to pass additional arguments
            download_func = partial(
                download_with_retry,
                download_folder=download_folder
            )

            # Limit concurrent downloads to avoid detection
            with ThreadPool(processes=3) as pool:
                pool.map(download_func, video_urls)

            zip_path = os.path.join(download_folder, "playlist.zip")
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for file in os.listdir(playlist_folder):
                    song_path = os.path.join(playlist_folder, file)
                    zipf.write(song_path, os.path.join("playlist", file))

            try:
                return send_file(zip_path, as_attachment=True)
            finally:
                shutil.rmtree(download_folder, ignore_errors=True)
        return {"status": "error", "message": "Invalid request format"}, 400

    except Exception as e:
        logger.error(f"Error in get_files route: {str(e)}")
        return {"status": "error", "message": "An error occurred during processing"}, 500


@app.route("/send_url/", methods=["POST"])
def send_url():
    try:
        url = request.json.get("url")

        # Basic validation
        if not url or "https://" not in url:
            return {"isFailed": True}

        # Parse the URL to check domain
        parsed_url = urlparse(url)
        if not parsed_url.netloc or 'youtube.com' not in parsed_url.netloc:
            return {"isFailed": True}

        # Add human-like delay
        HumanizedDownloader.add_human_delay()

        playlist_scraper = ChannelScraper(url)

        if not playlist_scraper.is_valid_url():
            return {"isFailed": True}

        session["url"] = url
        return {"isFailed": False}

    except Exception as e:
        logger.error(f"Error in send_url route: {str(e)}")
        return {"isFailed": True}


def download_with_retry(video_url, download_folder, max_retries=3):
    """Download video with retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Add a random delay between download attempts
            if attempt > 0:
                time.sleep(random.uniform(5, 10))

            # Get a random user agent for each download
            user_agent = HumanizedDownloader.get_random_user_agent()
            referer = HumanizedDownloader.get_random_referrer()

            # Configure YouTube with custom headers
            video = pytubefix.__main__.YouTube(
                video_url,
                use_po_token=True,
                po_token_verifier="MpQBNAu39XAyGiE0M666TURHZiLNVqcvy7E3LsQYcVK8-ZkAS5jKSoVNPcxiOo7VwOztVt5FRWyr3xEv8Vk9ztBxJLFNGdhWIuXaHbTB_BzmeW9yF7tEzlEzan7ZPwyCvzsXai5CUb2Jlx5ruCpGSBAeakzNJsWKoQ0DTz1bmFMOVUk-ykTZYR3KOzW4Cxm6CrdKiYDMag=="
            )

            # Set custom headers
            video.http_headers = {
                'User-Agent': user_agent,
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Referer': referer,
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
            }

            # Get stream and download with progressive sizes
            stream = video.streams.get_audio_only()
            if not stream:
                logger.warning(f"No audio stream available for {video_url}")
                return

            # Download the file
            output_path = os.path.join(download_folder, "playlist")
            file_path = stream.download(output_path)

            logger.info(f"Successfully downloaded: {os.path.basename(file_path)}")
            return

        except Exception as e:
            logger.error(f"Download attempt {attempt + 1} failed for {video_url}: {str(e)}")

            if attempt == max_retries - 1:
                logger.error(f"Failed to download {video_url} after {max_retries} attempts")


def fingerprint_prevention():
    """Apply prevention techniques for browser fingerprinting"""

    @app.after_request
    def add_header(response):
        # Disable caching
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        # Prevent browser fingerprinting
        response.headers[
            'Permissions-Policy'] = 'accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()'

        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        return response

    return None


if __name__ == '__main__':
    # Apply fingerprint prevention
    fingerprint_prevention()

    # Add a small random delay before starting the server
    time.sleep(random.uniform(0.5, 2.0))

    # Run with a randomly selected port in a common range to seem more natural
    port = random.randint(5000, 5050)
    app.run(host='0.0.0.0', port=port, threaded=True)