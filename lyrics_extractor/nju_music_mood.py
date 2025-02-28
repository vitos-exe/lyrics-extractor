import os
import shutil
import subprocess
from itertools import product
from pathlib import Path

import pandas as pd

from lyrics_extractor import constants


# For some reason the download link is not working with requests
def download_nju_music_mood():
    print("Downloading NJU-Music-Mood dataset(using curl)")
    subprocess.run(
        [
            "curl",
            "-L",
            constants.NJU_MUSIC_MOOD_DOWNLOAD_URL,
            "-o",
            f"{constants.NJU_MUSIC_MOOD_PATH}.zip",
        ]
    )
    file_name = f"{constants.NJU_MUSIC_MOOD_PATH}.zip"
    shutil.unpack_archive(file_name)
    os.remove(file_name)


def get_song_infos(root_directory):
    with open(root_directory / "info.txt", encoding="latin-1") as file:
        song_info_lists = filter(
            lambda l: len(l) == 3, map(lambda l: l.split(":")[:-1], file.readlines())
        )
    return {n: (t.strip(), a.strip()) for n, t, a in song_info_lists}


def get_songs_from_txts(root_directory, song_infos):
    for txt in root_directory.glob("*.txt"):
        if txt.name == "info.txt":
            continue

        file_name = txt.name.split(".")[0]
        label, number = file_name.split("_")
        if number not in song_infos:
            continue
        title, artist = song_infos[number]
        with open(txt, encoding="latin-1") as file:
            lyrics = file.read()

        yield {
            "title": title,
            "artist": artist,
            "lyrics": lyrics,
            "label": label,
        }


def get_nju_music_mood():
    if not os.path.exists(constants.NJU_MUSIC_MOOD_PATH):
        download_nju_music_mood()

    label_pathes = [
        path for path in Path(constants.NJU_MUSIC_MOOD_PATH).glob("*") if path.is_dir()
    ]

    all_songs = []
    for lp, phase in product(label_pathes, ["Train", "Test"]):
        current_folder = lp / phase
        song_infos = get_song_infos(current_folder)
        all_songs.extend(get_songs_from_txts(current_folder, song_infos))

    return pd.DataFrame(all_songs)
