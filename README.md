
# 🎵 Playlist Archiver (Alpha)

*A modern web interface for archiving YouTube playlists as audio collections*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.1.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Alpha Status](https://img.shields.io/badge/Status-Alpha-orange.svg)](https://semver.org/)

## 🌟 Features

### Current Alpha Capabilities
- 🎨 Clean Bootstrap-powered interface
- 🔍 Channel playlist discovery
- 📦 ZIP archive generation of audio content
- 🎧 MP4 audio extraction from YouTube videos
- 🔄 Session-based playlist management

### Planned Features
- 🚀 Dynamic channel URL input (Coming in v0.2)
- 🎚️ Audio quality selection
- 📤 Progressive download streaming
- 🔒 User authentication system

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- FFmpeg (for audio conversion)

```bash
# Clone repository
git clone https://github.com/yourusername/playlist-archiver.git
cd playlist-archiver

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

## 🚦 Usage

1. **Access Web Interface**  
   Navigate to `http://localhost:5000`
   
2. **Playlist Selection**  
   Browse available playlists from the demo channel

3. **Archive Generation**  
   Select a playlist to generate a downloadable ZIP archive

*Note: Currently configured with a demo channel - modify `session['url']` in `app.py` to test with different channels*

## 🧩 Project Structure

```
playlist-archiver/
├── app.py                 # Main application logic
├── ChannelScraper.py      # YouTube channel parser
├── templates/             # UI templates
│   ├── base.html          # Master template
│   └── playlistSelector.html # Playlist interface
└── downloads/             # Generated archives (auto-created)
```

## 🚧 Alpha Limitations

- 🔗 Hardcoded demo channel (dynamic input in development)
- ⚠️ Limited error handling
- 🛑 No parallel download queuing
- 📶 Basic audio quality selection

## 🤝 Contributing

We welcome contributors to help shape this alpha project! Here's how you can help:

1. **Report Issues**  
   [Open a new issue](https://github.com/yourusername/playlist-archiver/issues) for bugs or suggestions

2. **Feature Development**  
   Check our [Project Board](https://github.com/yourusername/playlist-archiver/projects/1) for prioritized tasks

3. **Code Standards**
   ```bash
   # Install development requirements
   pip install -r requirements-dev.txt
   
   # Run formatting check
   black --check .
   ```


---

**Disclaimer**: Use in compliance with YouTube's Terms of Service. This project is for educational purposes only.
