import argparse
import contextlib

import pandas as pd
import tqdm
from dotenv import load_dotenv

from . import constants, lyrics, moody_lyrics, nju_music_mood

load_dotenv()
tqdm.tqdm.pandas()

parser = argparse.ArgumentParser()
parser.add_argument("--moody-lyrics-version", choices=["raw", "balanced"], default="balanced")
args = parser.parse_args()

nju_df = nju_music_mood.get_nju_music_mood()

genius = lyrics.get_genius()
md_df = moody_lyrics.get_moody_lyrics(args.moody_lyrics_version)
with open("logs.txt", "w") as file:
    with contextlib.redirect_stdout(file):
        md_df["lyrics"] = md_df.progress_apply(
            lambda r: lyrics.get_lyrics(str(r["artist"]), str(r["title"]), genius),
            axis=1,
        )

pd.concat([nju_df, md_df], ignore_index=True).to_excel('lyrics.xlsx')