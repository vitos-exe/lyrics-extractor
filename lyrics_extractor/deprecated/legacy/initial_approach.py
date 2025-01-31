import os
import re
import shutil
import time
import warnings
from multiprocessing import Manager, Pool
from os import getenv

import pandas as pd
import spotify_lyrics_scraper as spotify
from dotenv import load_dotenv


def overwrite_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def create_dataset_folder_structure(root_folder_name, labels_names):
    overwrite_folder(root_folder_name)
    for ln in labels_names:
        overwrite_folder(f"{root_folder_name}/{ln}")


def save_lyrics(author, title, label, lyrics):
    author = re.sub(r"[&/\s]", "_", str(author).lower())
    title = re.sub(r"[&/\s]", "_", str(title).lower())
    save_title = f"{author}_{title}"
    file = f"{ROOT_DATA_FOLDER}/{label}/{save_title}.txt"
    with open(file, "w") as file:
        file.write("\n".join(lyrics))


def split_dataframe(df, chunk_size):
    chunks = []
    num_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size != 0 else 0)
    for i in range(num_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(df))
        chunks.append(df.iloc[start:end])
    return chunks


def get_lyrics(author, title, not_founds):
    load_dotenv()
    search_query = f"{author} - {title}".replace("&", "")
    try:
        token = spotify.getToken(getenv("SP_DC"))
        lyrics = spotify.getLyrics(token, songName=search_query)
        if not (lyrics["status"]):
            raise ValueError(lyrics["message"])
    except Exception as e:
        print(f"Retrieval failed for {search_query}\nReason: {e.args}", end="\n\n")
        not_founds.append(search_query)
        return ["ERROR", "\n".join(e.args)]

    print(f"{search_query} processed", end="\n\n")
    return [l["words"] for l in lyrics["message"]["lyrics"]["lines"]]


def get_batch_lyrics_async(authors_and_titles, not_founds):
    authors_and_titles_list = list(authors_and_titles)
    with Pool() as pool:
        all_lyrics = pool.starmap(
            get_lyrics, [song + (not_founds,) for song in authors_and_titles_list]
        )
    return all_lyrics


def main():
    warnings.warn("This module is deprecated", DeprecationWarning)

    ROOT_DATA_FOLDER = "lyrics_data"

    df = pd.read_excel("MoodyLyrics/ml_raw.xlsx")
    df = (
        df.iloc[15:, 1:]
        .reset_index()
        .drop("index", axis=1)
        .rename(
            {"Unnamed: 1": "author", "Unnamed: 2": "title", "Unnamed: 3": "label"},
            axis=1,
        )
    )

    manager = Manager()
    not_founds = manager.list()

    dfs = split_dataframe(df, 25)

    create_dataset_folder_structure(ROOT_DATA_FOLDER, df["label"].unique())

    for i, chunk in enumerate(dfs):
        print(f"Fetching lyrics for chunk {i + 1}/{len(dfs)}\n")
        lyrics = get_batch_lyrics_async(
            map(
                lambda r: (r[1]["author"], r[1]["title"]),
                chunk.iterrows(),
            ),
            not_founds,
        )
        for (_, row), l in zip(chunk.iterrows(), lyrics):
            save_lyrics(row["author"], row["title"], row["label"], l)
        time.sleep(5)

    with open("../../not_founds.txt", "w") as file:
        file.write("\n".join(not_founds))
