from danoan.perchance_tools.core import api, model


import argparse
import logging
from pathlib import Path
import pycountry
import sys
from typing import List
import yaml


import langchain

langchain.debug = True

LOG_LEVEL = logging.DEBUG

logger = logging.getLogger(__file__)
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(LOG_LEVEL)
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)


def __correct_words__(
    list_yml_filepath: List[str], language_name: str, *args, **kwargs
):
    language = pycountry.languages.get(name=language_name)
    if language is None:
        logger.error(f"Language {language} not recognized")
        exit(1)

    for yml_filepath in list_yml_filepath:
        yml_filepath = Path(yml_filepath)
        with open(yml_filepath, "r") as f_in:
            Y = yaml.load(f_in, Loader=yaml.Loader)
            word_dict = model.WordDict(Y)
            list_corrections = api.find_corrections(word_dict, language)
            corrected_dict = api.correct_words(word_dict, list_corrections)

            corrected_filename = f"corrected-{yml_filepath.name}"
            with open(corrected_filename, "w") as f_out:
                yaml.dump(corrected_dict.extract(), f_out, allow_unicode=True)


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

    parser.add_argument(
        "language_name", metavar="language", help="Language of the list of words."
    )
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
