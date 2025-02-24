import argparse
import pickle

import pandas as pd
import tqdm
from dotenv import load_dotenv
from joblib import Parallel, delayed

from . import lyrics, moody_lyrics, nju_music_mood
from .util import save_lyrics_by_label

load_dotenv()
tqdm.tqdm.pandas()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--moody-lyrics-version", choices=["raw", "balanced"], default="balanced"
)
parser.add_argument("--pickle-df", action="store_true")
args = parser.parse_args()

nju_df = nju_music_mood.get_nju_music_mood()

md_df = moody_lyrics.get_moody_lyrics(args.moody_lyrics_version)
md_df["lyrics"] = Parallel(n_jobs=-1)(
    delayed(lyrics.get_lyrics)(r["artist"], r["title"])
    for r in tqdm.tqdm(md_df.to_dict("records"), desc="Fetching lyrics")
)
md_df = md_df[md_df["lyrics"].notna()]

concatenated = pd.concat([nju_df, md_df], ignore_index=True)
save_lyrics_by_label(concatenated)

if args.pickle_df:
    with open("df.pkl", "wb") as f:
        pickle.dump(concatenated, f)
