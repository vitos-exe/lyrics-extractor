import os
import shutil

import pandas as pd
import requests

from . import constants


def download_moody_lyrics():
    print("Downloading MoodyLyrics dataset")
    response = requests.get(constants.MOODY_LYRICS_DOWNLOAD_URL)
    file_name = f"{constants.MOODY_LYRICS_PATH}.zip"
    with open(file_name, "wb") as file:
        file.write(response.content)
    shutil.unpack_archive(file_name)
    os.remove(file_name)


def cleanup_moody_lyrics(df):
    return (
        df.iloc[15:, 1:]
        .rename(
            columns={
                "Unnamed: 1": "artist",
                "Unnamed: 2": "title",
                "Unnamed: 3": "label",
            }
        )
        .reset_index(drop=True)
        .assign(
            artist=lambda d: d.artist.str.strip(), title=lambda d: d.title.str.strip()
        )
        .dropna()
    )


def get_moody_lyrics(version):
    if not os.path.exists(constants.MOODY_LYRICS_PATH):
        download_moody_lyrics()
    dataset_path = f"{constants.MOODY_LYRICS_PATH}/{constants.MOODY_LYRICS_FILE_TEMPLATE.format(version)}"
    df = pd.read_excel(dataset_path)
    return cleanup_moody_lyrics(df)
