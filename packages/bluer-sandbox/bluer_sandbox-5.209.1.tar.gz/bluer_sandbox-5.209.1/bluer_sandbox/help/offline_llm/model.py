from typing import List

from bluer_options.terminal import show_usage, xtra


def help_get(
    tokens: List[str],
    mono: bool,
) -> str:
    options_what = "filename | object_name | repo_name"

    options = "tiny"

    return show_usage(
        [
            "@offline_llm",
            "model",
            "get",
            f"[{options_what}]",
            f"[{options}]",
        ],
        "get model properties.",
        mono=mono,
    )


def help_download(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun,overwrite,tiny", mono=mono)

    return show_usage(
        [
            "@offline_llm",
            "model",
            "download",
            f"[{options}]",
        ],
        "download the model.",
        mono=mono,
    )


help_functions = {
    "download": help_download,
    "get": help_get,
}
