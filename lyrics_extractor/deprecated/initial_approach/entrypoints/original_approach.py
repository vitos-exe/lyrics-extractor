import pickle

import tqdm

from .. import dataset, lyrics, spotify


def main():
    try:
        with open(dataset.PICKLED_EXTENDED_DATAFRAME_PATH, "rb") as file:
            extended_df = pickle.load(file)
    except:
        sp = spotify.get_spotify_client()

        df = dataset.get_dataset()
        sampled_df = dataset.sample_dataset_equally(df)
        extended_df = spotify.get_with_title_and_artists(sampled_df, sp)

        with open(dataset.PICKLED_EXTENDED_DATAFRAME_PATH, "wb") as file:
            pickle.dump(extended_df, file)

    tqdm.tqdm.pandas()
    extended_df.progress_apply(lyrics.get_lyrics, axis=1)
