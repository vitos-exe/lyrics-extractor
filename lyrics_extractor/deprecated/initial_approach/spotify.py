from functools import reduce
from os import environ
from time import sleep

import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm


def get_spotify_client():
    client_id = environ.get("SPOTIFY_CLIENT_ID")
    client_secret = environ.get("SPOTIFY_CLIENT_SECRET")
    auth_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def get_title_and_artists(sp_track):
    return sp_track["name"], [artist["name"] for artist in sp_track["artists"]]


def get_with_title_and_artists(df: pd.DataFrame, sp: spotipy.Spotify):
    df_values = df["uri"].values
    chunks = np.array_split(df_values, len(df_values) // 50)

    def get_tracks_with_delay(chunk):
        sleep(0.5)
        return sp.tracks(chunk)["tracks"]

    sp_track_chunks = [get_tracks_with_delay(c) for c in tqdm(chunks)]
    sp_tracks = reduce(lambda xs, ys: xs + ys, sp_track_chunks)
    track_infos = [get_title_and_artists(sp_track) for sp_track in sp_tracks]
    track_infos_df = pd.DataFrame(track_infos, columns=["title", "artists"])
    return pd.concat(
        [
            df.reset_index().drop(columns=["index"]),
            track_infos_df.reset_index().drop(columns=["index"]),
        ],
        axis=1,
    )
