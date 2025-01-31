import os
import pickle
import shutil

import pandas as pd
from dotenv import load_dotenv

from lyrics_extractor import constants, lyrics, moody_lyrics, nju_music_mood


def save_lyrics_by_label(df, root_folder="lyrics"):
    os.makedirs(root_folder, exist_ok=True)

    for _, row in df.iterrows():
        label_dir = os.path.join(root_folder, row["label"])
        os.makedirs(label_dir, exist_ok=True)

        filename = f"{row['artist']} - {row['title']}.txt".replace("/", "&")
        filepath = os.path.join(label_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(row["lyrics"]))


def filter_existing_folder(df, root_folder="lyrics"):
    if not os.path.isdir(root_folder):
        return df
    existing = set()
    for label in os.listdir(root_folder):
        label_path = os.path.join(root_folder, label)
        if not os.path.isdir(label_path):
            continue
        for fname in os.listdir(label_path):
            if not fname.lower().endswith(".txt"):
                continue
            name = fname[:-4]
            parts = name.split(" - ", 1)
            if len(parts) != 2:
                continue
            existing.add((parts[0], parts[1]))
    mask = [
        (row["artist"].replace("/", "&"), row["title"].replace("/", "&"))
        not in existing
        for _, row in df.iterrows()
    ]
    return df[mask]


def combine_nju(df):
    nju_df = nju_music_mood.get_nju_music_mood()
    return pd.concat([nju_df, df], ignore_index=True)


def cleanup_downloads(paths):
    for path in paths:
        shutil.rmtree(path, ignore_errors=True)


def main(ml_version, to_pickle, include_nju, delete_downloads):
    load_dotenv()

    df = moody_lyrics.get_moody_lyrics(ml_version)
    if include_nju:
        df = combine_nju(df)
    df = filter_existing_folder(df)
    df = lyrics.get_all_lyrics(df)

    save_lyrics_by_label(df)

    if to_pickle:
        df.to_pickle("df.pkl")

    if delete_downloads:
        cleanup_downloads([constants.MOODY_LYRICS_PATH, constants.NJU_MUSIC_MOOD_PATH])
