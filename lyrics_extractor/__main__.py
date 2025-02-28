import argparse

from . import main

parser = argparse.ArgumentParser()
parser.add_argument(
    "--moody-lyrics-version", choices=["raw", "balanced"], default="balanced"
)
parser.add_argument("--pickle-df", action="store_true")
args = parser.parse_args()
main(args.moody_lyrics_version, args.pickle_df)
