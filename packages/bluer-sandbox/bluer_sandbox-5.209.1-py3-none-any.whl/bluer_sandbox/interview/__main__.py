import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_sandbox import NAME
from bluer_sandbox.interview.anagram import (
    normalize_and_group_and_analyze,
    count_anagrams_in_list,
)
from bluer_sandbox.tests.test_anagram_groups import words
from bluer_sandbox.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="anagram,group",
)
parser.add_argument(
    "--query",
    type=str,
)
args = parser.parse_args()

success = False
if args.task == "anagram":
    success = True

    dict_words = [
        "listen",
        "silent",
        "enlist",
        "google",
        "elbow",
        "below",
        "bowl",
        "stressed",
        "desserts",
        "dog",
        "god",
        "odg",
    ]
    queries = ["listen", "bowl", "dessert", "god", "cat"]

    print(count_anagrams_in_list(dict_words, queries))
if args.task == "group":
    success = True
    normalize_and_group_and_analyze(words)
else:
    success = None

sys_exit(logger, NAME, args.task, success)
