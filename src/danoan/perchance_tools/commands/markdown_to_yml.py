from danoan.perchance_tools.core import api

import argparse
import sys
from typing import List, TextIO
import yaml


def markdown_to_yml(markdown_stream: TextIO, output_stream: TextIO):
    """
    Convert markdown categorized file to yml.

    Given a list of words hierarchicaly categorized in markdown format,
    convert it to yaml.
    """
    D = api.create_dict_from_markdown(markdown_stream)
    yaml.dump(D.extract(), sys.stdout, allow_unicode=True)


def __markdown_to_yml__(list_markdown_filepath: List[str], *args, **kwargs):
    for filepath in list_markdown_filepath:
        with open(filepath, "r") as f:
            markdown_to_yml(f, sys.stdout)


def extend_parser(subparser_action=None):
    command_name = "markdown-to-yml"
    description = markdown_to_yml.__doc__
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
        "list_markdown_filepath",
        metavar="markdown_filepath",
        nargs="+",
        help="One or more path to hierarchicaly markdown file list of words.",
    )
    parser.set_defaults(func=__markdown_to_yml__, subcommand_help=parser.print_help)

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
