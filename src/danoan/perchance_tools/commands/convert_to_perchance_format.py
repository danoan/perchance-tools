from danoan.perchance_tools.core import api, model, utils

import argparse
import logging
import pycountry
import sys
import yaml

from typing import Any, Dict, List, TextIO

LOG_LEVEL = logging.INFO

logger = logging.getLogger(__file__)
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(LOG_LEVEL)
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)


def format_key_name(s):
    return s.lower().replace(",", " ").replace("  ", " ").replace(" ", "_")


def _key_path_to_perchance_dict(list_key_paths: List[Dict[str, Any]]):
    d = {"root": []}
    for key_path in list_key_paths:
        d["root"].append({})
        current = d["root"][-1]
        for key in key_path["path"]:
            perchance_key = format_key_name(key)
            if perchance_key not in current:
                current[perchance_key] = [{}]
            else:
                current[perchance_key].append({})

            current = current[perchance_key][-1]
        current["words"] = key_path["words"]
    return d


def _translate_key_paths(word_dict: model.WordDict):
    for key_path in utils.collect_key_path(word_dict, "words"):
        kp = {"path": [], "words": key_path["words"]}
        categories = key_path["path"]
        for category in categories:
            if category == "root":
                continue
            from_language = pycountry.languages.get(name="French")
            to_language = pycountry.languages.get(name="English")
            response = api.translate(category, from_language.name, to_language.name)
            if not response:
                logger.info(f"Error processing: {categories}. Skipping.")
                continue

            kp["path"].append(response[0])
        yield kp


def __convert_to_perchance_format__(list_yml_filepath: List[str], *args, **kwargs):
    """
    Convert one or more yml files containing a list of words in a perchance data structure.
    """
    for filepath in list_yml_filepath:
        with open(filepath, "r") as f:
            T = yaml.load(f, Loader=yaml.Loader)
            word_dict = model.WordDict(T)

            d = _key_path_to_perchance_dict(list(_translate_key_paths(word_dict)))
            yaml.dump(d, sys.stdout, allow_unicode=True)


def extend_parser(subparser_action=None):
    command_name = "convert-to-perchance"
    description = __convert_to_perchance_format__.__doc__
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
        "list_yml_filepath",
        metavar="yml_filepath",
        nargs="+",
        help="One or more path to yml file list of words.",
    )
    parser.set_defaults(
        func=__convert_to_perchance_format__, subcommand_help=parser.print_help
    )

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
