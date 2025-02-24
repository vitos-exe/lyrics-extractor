import contextlib
import os

from typing_extensions import Callable, TypeVar


def fail_retry(limit=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            local_limit = limit
            last_exception = None
            while local_limit:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print("---Retrying...")
                    last_exception = e
                local_limit -= 1
            return f"ERROR\n{repr(last_exception)}"

        return wrapper

    return decorator


T = TypeVar("T")


def with_stdout_redirect(func: Callable[..., T], *args, **kwargs) -> T:
    with open(f"{func.__name__}.txt", "w") as f:
        with contextlib.redirect_stdout(f):
            return func(*args, **kwargs)


def save_lyrics_by_label(df, root_folder="lyrics"):
    os.makedirs(root_folder, exist_ok=True)

    for _, row in df.iterrows():
        label_dir = os.path.join(root_folder, row["label"])
        os.makedirs(label_dir, exist_ok=True)

        filename = f"{row['artist']} - {row['title']}.txt".replace("/", "&")
        filepath = os.path.join(label_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(row["lyrics"]))
