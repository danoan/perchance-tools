import argparse
import copy
from jinja2 import Environment, PackageLoader
import logging
from pathlib import Path
import sys
import yaml

from typing import List, Optional

SCRIPT_FOLDER = Path(__file__).parent

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)

env = Environment(loader=PackageLoader("danoan.perchance_tools", "assets/templates"))


def render_prompt(categories: List[str], words: List[str]):
    template = env.get_template("correct-words-user.txt.tpl")
    return template.render(categories=categories, words=words)


def __correct_words__(list_yml_filepath: List[str], language: str, *args, **kwargs):
    """
    Find mispellings in a list of words and correct them.

    Each item in list_yml_filepath must be a path to a yml file with the following schema:

    ```yml
    key: "root"
    values:
    - key: "Category_A"
      values:
      - key: "Category_B1"
        values:
        - key: "words"
          values:
          - word_a
          - word_b
          - word_c
      - key: "Category_B2"
        values:
        - key: "words"
          values:
          - word_d
          - word_e
    ```
    """

    def __traverse__(T, categories):
        key = T["key"]
        values = T["values"]

        if key == "words":
            yield {"categories": categories, "words": values}
        else:
            categories.append(key)

            if type(values) is dict:
                for x in __traverse__(values, categories):
                    yield x
            else:
                for next in values:
                    for x in __traverse__(next, categories):
                        yield x

            categories.pop()

    def traverse(T):
        for x in __traverse__(T, []):
            yield x

    for yml_filepath in list_yml_filepath:
        with open(yml_filepath, "r") as f:
            T = yaml.load(f, Loader=yaml.Loader)

            for data_dict in traverse(T):
                dict_copy = copy.deepcopy(data_dict)
                dict_copy["categories"].remove("root")
                print(render_prompt(**dict_copy))


def extend_parser(subparser_action=None):
    command_name = "correct-words"
    description = __correct_words__.__doc__
    help = description.split(".")[0] if description else ""

    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            help=help,
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument("language", help="Language of the list of words.")
    parser.add_argument(
        "list_yml_filepath",
        metavar="yml_filepath",
        nargs="+",
        help="One or more path to yml file list of words.",
    )
    parser.set_defaults(func=__correct_words__, subcommand_help=parser.print_help)

    return parser


def main():
    parser = extend_parser()
    args = parser.parse_args()

    if "func" in args:
        args.func(**vars(args))
    elif "subcommand_help" in args:
        args.subcommand_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
