import os

from bluer_options.help.functions import get_help
from bluer_objects import file, README

from bluer_sandbox import NAME, VERSION, ICON, REPO_NAME
from bluer_sandbox.help.functions import help_functions


items = README.Items(
    [
        {
            "name": "arvancloud",
            "description": "tools to work with [arvancloud](https://arvancloud.ir/).",
            "marquee": "https://github.com/kamangir/assets/blob/main/arvancloud/arvancloud.png?raw=true",
            "url": "./bluer_sandbox/docs/arvancloud.md",
        },
        {
            "name": "tor",
            "description": "tools to work with [tor](https://www.torproject.org/).",
            "marquee": "https://github.com/kamangir/assets/blob/main/tor/tor2.png?raw=true",
            "url": "./bluer_sandbox/docs/tor.md",
        },
        {
            "name": "offline LLM",
            "description": "using [llama.cpp](https://github.com/ggerganov/llama.cpp).",
            "marquee": "https://user-images.githubusercontent.com/1991296/230134379-7181e485-c521-4d23-a0d6-f7b3b61ba524.png",
            "url": "./bluer_sandbox/docs/offline_llm.md",
        },
    ]
)


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            cols=readme.get("cols", 3),
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
        )
        for readme in [
            {
                "path": "..",
                "items": items,
            },
        ]
        + [
            {"path": f"docs/{doc}.md"}
            for doc in [
                "arvancloud",
                "offline_llm",
                "LSTM",
                "tor",
            ]
        ]
        + [{"path": "docs"}]
        + [{"path": "docs/aliases"}]
        + [
            {"path": f"docs/aliases/{alias}.md"}
            for alias in [
                "arvancloud",
                "assets",
                "docker",
                "notebooks",
                "offline_llm",
                "speedtest",
                "tor",
            ]
        ]
    )
