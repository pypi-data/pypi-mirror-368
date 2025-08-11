from typing import List

from bluer_options.terminal import show_usage, xtra


def help_seed(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("screen", mono=mono)

    return show_usage(
        [
            "@arvan",
            "seed",
            f"[{options}]",
        ],
        "seed 🌱  arvancloud.",
        mono=mono,
    )


def help_ssh(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun,~seed", mono=mono)

    return show_usage(
        [
            "@arvan",
            "ssh",
            f"[{options}]",
            "<ip-address>",
        ],
        "ssh to arvancloud.",
        mono=mono,
    )


help_functions = {
    "seed": help_seed,
    "ssh": help_ssh,
}
