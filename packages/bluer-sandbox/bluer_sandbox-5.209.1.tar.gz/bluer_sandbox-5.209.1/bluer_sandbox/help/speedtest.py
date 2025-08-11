from typing import List

from bluer_options.terminal import show_usage, xtra


def help_speedtest(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun,~install", mono=mono)

    return show_usage(
        [
            "@speedtest",
            f"[{options}]",
        ],
        "speedtest.",
        mono=mono,
    )
