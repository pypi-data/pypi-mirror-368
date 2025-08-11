from bluer_ai.help.generic import help_functions as generic_help_functions
from bluer_sandbox.help.arvancloud import help_functions as help_arvancloud
from bluer_sandbox.help.assets import help_functions as help_assets
from bluer_sandbox.help.docker import help_functions as help_docker
from bluer_sandbox.help.interview import help_functions as help_interview
from bluer_sandbox.help.notebooks import help_functions as help_notebooks
from bluer_sandbox.help.offline_llm import help_functions as help_offline_llm
from bluer_sandbox.help.parser import help_functions as help_offline_parser
from bluer_sandbox.help.speedtest import help_speedtest
from bluer_sandbox.help.tor import help_functions as help_tor

from bluer_sandbox import ALIAS


help_functions = generic_help_functions(plugin_name=ALIAS)

help_functions.update(
    {
        "arvancloud": help_arvancloud,
        "assets": help_assets,
        "docker": help_docker,
        "interview": help_interview,
        "notebooks": help_notebooks,
        "offline_llm": help_offline_llm,
        "parser": help_offline_parser,
        "speedtest": help_speedtest,
        "tor": help_tor,
    }
)
