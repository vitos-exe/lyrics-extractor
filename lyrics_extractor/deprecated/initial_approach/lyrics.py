from enum import Enum
from os import environ
from time import sleep

import pandas as pd
import requests
import spotify_lyrics_scraper

TOKEN = None


def get_token():
    global TOKEN
    if TOKEN is None:
        sp_dc = environ.get('SP_DC')
        sp_key = environ.get('SP_KEY')
        TOKEN = spotify_lyrics_scraper.getToken(sp_dc, sp_key)
        pass
    return TOKEN


def fetch_lyrics_with_spotify_lyrics_scraper(id):
    token = get_token()
    lyrics = spotify_lyrics_scraper.getLyrics(token, trackId=id)
    if not lyrics['status']:
        return ErrorType.TOO_MANY_REQUESTS if '429' in lyrics['message'] else ErrorType.NOT_FOUND
    formatted_lyrics = '\n'.join(lyrics.formatLyrics()['message'])
    return formatted_lyrics


def fetch_lyrics_with_ovh(artist, title):
    url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return data['lyrics']


def get_lyrics(extended_df_row: pd.Series):
    sleep(2)
    uri, title, artists = extended_df_row['uri'], extended_df_row['title'], ', '.join(extended_df_row['artists'])
    lyrics = fetch_lyrics_with_spotify_lyrics_scraper(uri)
    if type(lyrics) == str:
        return lyrics
    lyrics = fetch_lyrics_with_ovh(artists, title)
    return lyrics


class ErrorType(Enum):
    NOT_FOUND = 1
    TOO_MANY_REQUESTS = 2
