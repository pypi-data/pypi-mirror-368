from typing import List

from bluer_options.terminal import show_usage


def help_timestamp(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@timestamp",
        ],
        "timestamp.",
        mono=mono,
    )


def help_timestamp_short(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@@timestamp",
        ],
        "short timestamp.",
        mono=mono,
    )


help_functions = {
    "timestamp": {
        "": help_timestamp,
        "short": help_timestamp_short,
    }
}
