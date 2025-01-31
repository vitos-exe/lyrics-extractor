import sys
import threading
from functools import partial
from typing import Union

import lyricsgenius
import pandas as pd
import requests
from joblib import Parallel, delayed
from requests import RequestException
from tqdm import tqdm

from . import constants

_genius_lock = threading.Lock()

def get_lyrics_genius(genius: lyricsgenius.Genius, artist, title):
    try:
        with _genius_lock:
            genius_artist = genius.search_artist(artist, max_songs=0)
            genius_song = genius.search_song(title, genius_artist.name, get_full_info=False)
        return genius_song.lyrics
    except Exception as error:
        tqdm.write(f"Genius request failed: {error}\n")
        return None

def get_lyrics_ovh(artist: str, title: str, timeout: float = 5.0) -> Union[str, None]:
    url = f"{constants.OVH_URL}/{artist}/{title}"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("lyrics")
    except RequestException as err:
        tqdm.write(f"OVH request failed: {err}\n")
    except ValueError as err:
        tqdm.write(f"Invalid JSON response from OVH: {err}\n")
    return None

@delayed
def get_lyrics(artist, title, genius=None):
    """
    Try OVH first, then fall back to Genius if provided.
    Returns lyrics string or None.
    """
    tqdm.write(f"Fetching lyrics for {artist} – {title}\n")

    sources = [
        ("OVH", partial(get_lyrics_ovh, artist, title)),
    ]
    if genius is not None:
        sources.append(("Genius", partial(get_lyrics_genius, genius, artist, title)))

    for name, fetch in sources:
        tqdm.write(f"— Trying {name!r}…\n")
        lyrics = fetch()
        if lyrics:
            tqdm.write(f"— {name!r} succeeded!\n")
            return lyrics
        tqdm.write(f"— {name!r} failed\n")

    tqdm.write("— All sources exhausted; no lyrics found\n")
    return None

def get_all_lyrics(df: pd.DataFrame) -> pd.DataFrame:
    genius = lyricsgenius.Genius(timeout=15, retries=3, sleep_time=1)
    all_lyrics = Parallel(n_jobs=-1, backend='threading')(
        get_lyrics(r["artist"], r["title"], genius=genius)
        for r in tqdm(df.to_dict("records"), desc="Fetching lyrics")
    )
    return df.assign(lyrics=all_lyrics)
