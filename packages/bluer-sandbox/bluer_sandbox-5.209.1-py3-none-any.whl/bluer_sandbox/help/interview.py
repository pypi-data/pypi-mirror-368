from typing import List

from bluer_options.terminal import show_usage


def help(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@sandbox",
            "interview",
            "<what>",
            "<args>",
        ],
        "interview/<what> <args>.",
        mono=mono,
    )


help_functions = {
    "": help,
}
