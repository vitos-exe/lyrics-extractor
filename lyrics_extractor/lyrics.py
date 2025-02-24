import lyricsgenius
import requests

from . import constants, util
from .util import with_stdout_redirect


def get_genius():
    return lyricsgenius.Genius(timeout=15, retries=3)


@util.fail_retry()
def get_lyrics_genius(genius, artist, title):
    genius_artist = genius.search_artist(artist, max_songs=0)
    genius_song = genius.search_song(title, genius_artist.name, get_full_info=False)
    return genius_song.lyrics


@util.fail_retry()
def get_lyrics_ovh(artist, title):
    response = requests.get(f"{constants.OVH_URL}/{artist}/{title}")
    if response.status_code == 200:
        return response.json()["lyrics"]
    elif response.status_code == 404:
        return None
    else:
        raise Exception(f"Lyrics API returned {response.status_code}")


def get_lyrics(artist, title, genius=None):
    print(f"--------Getting lyrics for {title} from {artist}")

    print("--------Trying to use OVH...")
    song_lyrics = get_lyrics_ovh(artist, title)
    if song_lyrics is None:
        print("--------OVH didn't find any lyrics")
        if genius is not None:
            print("--------Trying to use Genius...")
            song_lyrics = with_stdout_redirect(get_lyrics_genius, genius, artist, title)
            print("--------Genius found lyrics")
    else:
        print("--------OVH found lyrics")
    print(2 * "\n")
    return song_lyrics
