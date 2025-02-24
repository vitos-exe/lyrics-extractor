from os import path

import kagglehub
import pandas as pd

DATASET_NAME = "abdullahorzan/moodify-dataset"
DATASET_FILE_NAME = "278k_labelled_uri.csv"
PICKLED_EXTENDED_DATAFRAME_PATH = "pickled/extended_df.pkl"


def get_dataset():
    dataset_path = path.join(
        kagglehub.dataset_download(DATASET_NAME), DATASET_FILE_NAME
    )
    return pd.read_csv(dataset_path)[["labels", "uri"]]


def sample_dataset_equally(dataframe, samples_per_class=2500) -> pd.DataFrame:
    sampled = dataframe.groupby("labels").sample(n=samples_per_class)
    sampled["uri"] = sampled["uri"].map(lambda u: u.split(":")[2])
    return sampled
