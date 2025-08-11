import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_sandbox import NAME
from bluer_sandbox.offline_llm.model.functions import get
from bluer_sandbox.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="get",
)
parser.add_argument(
    "--what",
    type=str,
    help="filename | object_name | repo_name",
    default="object",
)
parser.add_argument(
    "--tiny",
    type=int,
    help="0 | 1",
    default=0,
)
args = parser.parse_args()

success = False
if args.task == "get":
    success = True
    print(
        get(
            what=args.what,
            tiny=args.tiny == 1,
        )
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
