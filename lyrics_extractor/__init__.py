import pickle

import pandas as pd
from dotenv import load_dotenv
from joblib import Parallel, delayed
from tqdm import tqdm

from lyrics_extractor import nju_music_mood, moody_lyrics, lyrics
from lyrics_extractor.util import save_lyrics_by_label


def main(ml_version, to_pickle):
    load_dotenv()
    tqdm.pandas()

    nju_df = nju_music_mood.get_nju_music_mood()

    md_df = moody_lyrics.get_moody_lyrics(ml_version)
    md_df["lyrics"] = Parallel(n_jobs=-1)(
        delayed(lyrics.get_lyrics)(r["artist"], r["title"])
        for r in tqdm(md_df.to_dict("records"), desc="Fetching lyrics")
    )
    md_df = md_df[~md_df["lyrics"].str.startswith("ERROR")]

    concatenated = pd.concat([nju_df, md_df], ignore_index=True)
    save_lyrics_by_label(concatenated)

    if to_pickle:
        with open("df.pkl", "wb") as f:
            pickle.dump(concatenated, f)
