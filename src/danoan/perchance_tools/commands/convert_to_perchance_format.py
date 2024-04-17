import argparse
import json
import yaml
import sys

from typing import List, TextIO


def translate_text(text: str, from_language: str, to_language: str):
    pass


def format_key_name(s):
    return s.lower().replace(" ", "_")


def dump_perchance_format(obj, stream_out: TextIO):
    def _dump(obj, indentation_level: int):
        original_key = obj["key"]

        if original_key != "words":
            translation_response = json.loads(
                translate_text(original_key.lower(), "fra", "eng")
            )
            if len(translation_response) == 0:
                print("ERROR: No translation for word:", original_key)
            else:
                translated_key = translation_response[0]

            stream_out.write(" " * indentation_level * 4)
            stream_out.write(f"{format_key_name(translated_key)}\n")
            indentation_level += 1

            stream_out.write(" " * indentation_level * 4)
            stream_out.write(f"name={original_key}\n")

        for value in obj["values"]:
            if type(value) is dict:
                _dump(value, indentation_level + 1)
            else:
                stream_out.write(" " * indentation_level * 4)
                stream_out.write(f"{value}\n")

    _dump(obj, 0)


def __convert_to_perchance_format__(list_yml_filepath: List[str], *args, **kwargs):
    """
    Convert one or more yml files containing a list of words in a perchance data structure.
    """
    for filepath in list_yml_filepath:
        with open(filepath, "r") as f:
            T = yaml.load(f, Loader=yaml.Loader)
            dump_perchance_format(T, sys.stdout)


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
