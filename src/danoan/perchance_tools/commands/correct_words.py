from danoan.perchance_tools.core import api, exception, model
from danoan.llm_assistant.core.api import LLM_ASSISTANT_ENV_VARIABLE

import argparse
import logging
import os
from pathlib import Path
import pycountry
import sys
from typing import List, TextIO, Text
import yaml

LOG_LEVEL = logging.INFO

logger = logging.getLogger(__file__)
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(LOG_LEVEL)
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)


def correct_words(yml_stream: TextIO, language: Text) -> model.WordDict:
    Y = yaml.load(yml_stream, Loader=yaml.Loader)
    word_dict = model.WordDict(Y)
    list_corrections = api.find_corrections(word_dict, language)
    corrected_dict = api.replace_words(word_dict, list_corrections)
    return corrected_dict


def __correct_words__(
    list_yml_filepath: List[str], language_name: str, *args, **kwargs
):
    language = pycountry.languages.get(name=language_name)
    if language is None:
        logger.error(f"Language {language} not recognized")
        exit(1)

    for _yml_filepath in list_yml_filepath:
        yml_filepath = Path(_yml_filepath)
        with open(yml_filepath, "r") as f_in:
            try:
                corrected_dict = correct_words(f_in, language)
            except exception.CacheNotConfiguredError:
                print(
                    "The cache for LLM calls is not configured. Please setup",
                    " the llm-assistant with llm-assistant setup before proceeding",
                )
                exit(1)
            yaml.dump(corrected_dict.extract(), sys.stdout, allow_unicode=True)


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
