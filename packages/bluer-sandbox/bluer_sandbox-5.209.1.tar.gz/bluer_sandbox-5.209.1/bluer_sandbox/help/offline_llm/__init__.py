from typing import List

from bluer_options.terminal import show_usage, xtra

from bluer_sandbox.help.offline_llm.model import help_functions as help_model


def help_build(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun", mono=mono)

    return show_usage(
        [
            "@offline_llm",
            "build",
            f"[{options}]",
        ],
        "build offline_llm.",
        mono=mono,
    )


def help_chat(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("download_model,tiny,~upload", mono=mono)

    return show_usage(
        [
            "@offline_llm",
            "chat",
            f"[{options}]",
            "[-|<object-name>]",
        ],
        "chat with offline_llm.",
        mono=mono,
    )


def help_create_env(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@plugin",
            "create_env",
        ],
        "create env.",
        mono=mono,
    )


def help_prompt(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "".join(
        [
            xtra("download_model,tiny,", mono=mono),
            "upload",
        ]
    )

    return show_usage(
        [
            "@offline_llm",
            "prompt",
            f"[{options}]",
            '"<prompt>"',
            "[-|<object-name>]",
        ],
        '"<prompt>" -> offline_llm.',
        mono=mono,
    )


help_functions = {
    "build": help_build,
    "chat": help_chat,
    "create_env": help_create_env,
    "model": help_model,
    "prompt": help_prompt,
}
