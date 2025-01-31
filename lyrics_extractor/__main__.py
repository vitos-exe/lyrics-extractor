import argparse
import contextlib

import tqdm
from dotenv import load_dotenv

from . import constants
from . import lyrics
from . import moody_lyrics

load_dotenv()
tqdm.tqdm.pandas()

parser = argparse.ArgumentParser()
parser.add_argument("--dataset", choices=['raw', 'balanced'], default='balanced')
args = parser.parse_args()

genius = lyrics.get_genius()
df = moody_lyrics.get_moody_lyrics(args.dataset)
with open('logs.txt', 'w') as file:
    with contextlib.redirect_stdout(file):
        df['lyrics'] = df.progress_apply(lambda r: lyrics.get_lyrics(str(r['artist']), str(r['title']), genius), axis=1)
df.to_csv(constants.OUTPUT_DATA_PATH)
