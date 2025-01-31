from time import sleep

import pandas as pd

from .. import dataset, lyrics

LABELS = [0, 1, 2, 3]
LIMIT = 1250
DATA_PATH = "data.csv"


def label_is_full(df, label):
    vc = df["label"].value_counts()
    return label in vc and vc[label] == LIMIT


def labels_are_full(df):
    return all(label_is_full(df, l) for l in LABELS)


def get_with_row(df, row):
    return pd.concat([df, pd.DataFrame([row], columns=df.columns)], ignore_index=True)


def pretty_print_label_counts(df):
    vc = df["label"].value_counts()
    print("Label counts")
    for label, count in vc.items():
        print(f"{label} --- {count:04}/{LIMIT}")


def get_original_and_data_df():
    original_df = dataset.get_dataset()
    try:
        saved_data = pd.read_csv(DATA_PATH)
        last_row_original_index = saved_data.iloc[-1]["original_index"]
        return original_df.iloc[last_row_original_index + 1 :], saved_data
    except:
        return original_df, pd.DataFrame(
            columns=["label", "uri", "lyrics", "original_index"]
        )


def main():
    original_df, df = get_original_and_data_df()
    index = 0
    while not labels_are_full(df):
        row = original_df.iloc[index]
        original_index = row.name

        label = row["labels"]
        if label_is_full(df, label):
            continue

        uri = row["uri"].split(":")[2]

        try:
            lyrics_data = lyrics.fetch_lyrics_with_spotify_lyrics_scraper(uri)
        except:
            print("ERROR")
            print(3 * "\n")
            index -= 1
            continue

        if lyrics_data is lyrics.ErrorType.TOO_MANY_REQUESTS:
            print("Too many requests, waiting 10 seconds")
            sleep(10)
            continue
        elif lyrics_data is lyrics.ErrorType.NOT_FOUND:
            print(f"Data was not found for id {uri} and label {label}")

        else:
            print(f"Found data for id {uri} and label {label}")
            df = get_with_row(df, [label, uri, lyrics_data, original_index])
            df.to_csv(DATA_PATH, index=False)

        pretty_print_label_counts(df)
        print(3 * "\n")
        sleep(4)
        index += 1
