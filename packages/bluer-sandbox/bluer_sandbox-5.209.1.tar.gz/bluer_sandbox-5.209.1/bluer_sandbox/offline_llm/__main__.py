import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_sandbox import NAME
from bluer_sandbox.offline_llm.functions import post_process
from bluer_sandbox.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="post_process",
)
parser.add_argument(
    "--object_name",
    type=str,
)
args = parser.parse_args()

success = False
if args.task == "post_process":
    success = post_process(object_name=args.object_name)
else:
    success = None

sys_exit(logger, NAME, args.task, success)
