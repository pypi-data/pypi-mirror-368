from typing import List

from bluer_options.terminal import show_usage, xtra


def help_publish(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "".join(
        [
            xtra("download,", mono=mono),
            "extensions=png+txt",
            xtra(",~pull,", mono=mono),
            "push",
        ]
    )

    args = [
        "[--asset_name <other-object-name>]",
        "[--prefix <prefix>]",
    ]

    return show_usage(
        [
            "@assets",
            "publish",
            f"[{options}]",
            "[.|<object-name>]",
        ]
        + args,
        "<object-name>/<prefix> -> assets.",
        mono=mono,
    )


help_functions = {
    "publish": help_publish,
}
