import argparse

from dotenv import load_dotenv

from .entrypoints import ENTRYPOINTS

if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("entrypoint")
    args = parser.parse_args()
    entrypoint_name = args.entrypoint

    ENTRYPOINTS.get(entrypoint_name).main()
