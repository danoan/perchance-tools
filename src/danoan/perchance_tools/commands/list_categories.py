from danoan.perchance_tools.core import model, utils

import argparse
import logging
import sys
import yaml

from typing import Dict, List, TextIO

LOG_LEVEL = logging.INFO

logger = logging.getLogger(__file__)
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(LOG_LEVEL)
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)


def __list_categories__(yml_filepath: str, *args, **kwargs):
    with open(yml_filepath, "r") as f:
        word_dict = model.WordDict(yaml.load(f, Loader=yaml.Loader))
        # l = list(utils.collect_key_path(word_dict, "words"))
        # print(l)
        for key_path in utils.collect_key_path(word_dict, "words"):
            print(key_path["path"])


def extend_parser(subparser_action=None):
    command_name = "list-categories"
    description = __list_categories__.__doc__
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

    parser.add_argument(
        "yml_filepath",
        metavar="yml_filepath",
        help="Path to yml file list of words.",
    )
    parser.set_defaults(func=__list_categories__, subcommand_help=parser.print_help)

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
