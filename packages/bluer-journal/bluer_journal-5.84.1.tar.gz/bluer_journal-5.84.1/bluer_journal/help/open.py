from typing import List

from bluer_options.terminal import show_usage


def help_open(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@journal",
            "open",
            "[home | <YYYY-MM-DD>]",
        ],
        "open journal.",
        mono=mono,
    )
