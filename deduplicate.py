#!/usr/bin/env python3
import argparse
import hashlib
import os


def hash_file(path, chunk_size=8192):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def process_txt(root_dir, delete=False):
    seen = {}
    for dirpath, _, files in os.walk(root_dir):
        for name in sorted(files):
            if not name.lower().endswith(".txt"):
                continue
            full = os.path.join(dirpath, name)
            h = hash_file(full)
            if h in seen:
                print(f"Duplicate: {full} (same as {seen[h]})")
                if delete:
                    os.remove(full)
                    print(f"Deleted:   {full}")
            else:
                seen[h] = full


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Find (and optionally delete) duplicate .txt files"
    )
    p.add_argument("folder", help="Root directory to scan")
    p.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Delete duplicates, keep only first occurrence",
    )
    args = p.parse_args()
    process_txt(args.folder, delete=args.delete)
