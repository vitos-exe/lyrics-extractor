# Lyrics Extractor

A Python tool to fetch and combine song lyrics for MoodyLyrics/NJU datasets using OVH API, and Genius API.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m lyrics_extractor --moody-lyrics-version balanced [--include-nju] [--delete-downloads] [--pickle-df]
```

Results are saved to `lyrics` by default.
