import pickle

from .. import dataset


def test():
    global extended_df
    global uris
    global fetch_lyrics_with_spotify_lyrics_scraper

    with open(dataset.PICKLED_EXTENDED_DATAFRAME_PATH, "rb") as file:
        extended_df = pickle.load(file)

    uris = extended_df["uri"].values
