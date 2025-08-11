from typing import Dict, List, Any
import string
import numpy as np

from blueness import module

from bluer_sandbox import NAME
from bluer_sandbox.logger import logger


NAME = module.name(__file__, NAME)


def is_anagram(word_1, word_2) -> bool:
    return sorted(list(word_1)) == sorted(list(word_2))


def normalize_and_group_and_analyze(words: List[str]):
    logger.info("processing the words: {}".format(", ".join(words)))
    words = normalize_input(words)
    logger.info("normalized to: {}".format(", ".join(words)))

    groups = group_anagrams(words)
    logger.info(f"groups {groups}")

    stats = analyze_groups(groups)

    print_report(groups, stats)


def normalize_input(words: List[str]) -> List[str]:
    # Trims, lowercases, and filters out non-alphabetic words.
    # Returns a clean list of valid words.
    return [
        word
        for word in [word.strip().lower() for word in words]
        if all(character in string.ascii_lowercase for character in word) and word
    ]


def group_anagrams(words: List[str]) -> Dict[str, List[str]]:
    # Groups normalized words into anagram clusters.
    # Uses sorted letters as the key.
    groups: Dict[str, List[str]] = {}

    for word in words:
        found: bool = False
        for keyword, group in groups.items():
            if is_anagram(word, keyword):
                group.append(word)
                found = True
                break

        if not found:
            keyword = "".join(list(word))
            groups[keyword] = [word]

    return groups


def analyze_groups(groups: Dict[str, List[str]]) -> Dict[str, Any]:
    # Returns statistics:
    # total_groups
    # largest_group
    # average_group_size
    stats: Dict[str, Any] = {
        "total_groups": len(groups),
    }

    largest_group_size = max(len(group) for group in groups.values())
    largest_group_keyword = [
        keyword for keyword, group in groups.items() if len(group) == largest_group_size
    ]
    stats["largest_group"] = largest_group_keyword[0] if largest_group_keyword else ""

    stats["average_group_size"] = float(
        np.mean(np.array([len(group) for group in groups.values()]))
    )

    return stats


def group_as_str(group: List[str]) -> str:
    return "[{}]".format(", ".join(group))


def print_report(
    groups: Dict[str, List[str]],
    stats: Dict[str, Any],
):
    # Outputs a nicely formatted report, with:
    # Total groups
    # Average group size
    # Largest group
    # All anagram clusters sorted by the first element in each

    logger.info("Total groups: {}".format(stats["total_groups"]))

    logger.info("Average group size: {:.2f}".format(stats["average_group_size"]))

    largest_group_keyword = stats["largest_group"]
    logger.info(
        "Largest group (size {}): {}".format(
            len(groups[largest_group_keyword]),
            group_as_str(groups[largest_group_keyword]),
        )
    )

    logger.info("Anagram groups:")
    for group in groups.values():
        logger.info(group_as_str(group))


def count_anagrams_in_list(
    dictionary: List[str],
    query: List[str],
) -> List[int]:
    return [count_anagrams(dictionary, query_string) for query_string in query]


def count_anagrams(
    dictionary: List[str],
    query_string: str,
) -> int:
    logger.info(f"dictionary: {dictionary}")
    logger.info(f"query_string: {query_string}")

    count = 0
    for word in dictionary:
        if is_anagram(word, query_string):
            count += 1

    return count
