from danoan.perchance_tools.commands import (
    convert_to_perchance_format,
    correct_words,
    list_categories,
    markdown_to_yml,
)

import argparse
from textwrap import dedent


def main():
    command_name = "perchance-tools"
    description = dedent(
        """
    Collection of tools to write files in the perchance language.

    This program contains several scripts to help with the creation
    of perchance files. Perchance is a language that facilitates the
    generation of natural text in several languages.

    The main purpose of this script is to transform a list of words
    into perchance data structures. The assumption is that the list of
    words was provided from a thesaurus in markdown format.
    """
    )
    parser = argparse.ArgumentParser(
        command_name,
        description=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparser_action = parser.add_subparsers()

    list_of_commands = [
        markdown_to_yml,
        correct_words,
        convert_to_perchance_format,
        list_categories,
    ]
    for command in list_of_commands:
        command.extend_parser(subparser_action)

    args = parser.parse_args()
    if "func" in args:
        args.func(**vars(args))
    elif "subcommand_help" in args:
        args.subcommand_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
