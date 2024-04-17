import argparse
from pathlib import Path
import re
import sys
import yaml
from typing import List, TextIO


def collect_markers(markdown_text: str):
    header_start = re.compile(r"^[ ]*(#+)\s*([^\n]*)", re.MULTILINE)

    for m in header_start.finditer(markdown_text):
        header_marker, header_title = m.groups()
        header_level = len(header_marker)
        yield (header_level, header_title, m.span())


def create_tree_cues(markdown_text: str):
    m = list(collect_markers(markdown_text))
    m.append((0, 0, (len(markdown_text), len(markdown_text))))

    for e, n in zip(m[:-1], m[1:]):
        level, title, span = e
        _, _, next_span = n

        start, end = span
        next_start, _ = next_span

        words = []
        for w in markdown_text[end:next_start].split("\n"):
            _w = w.strip()
            if len(_w) == 0:
                continue
            words.append(_w)

        yield ([level, title, words, False])


def create_tree(markdown_text: str):
    cues = [[0, "root", [], False]]
    cues.extend(list(create_tree_cues(markdown_text)))

    def _create_tree(start_index: int):
        level, title, words, visited = cues[start_index]
        if visited:
            return None

        cues[start_index][3] = True
        root = {"key": title.strip(), "values": []}
        if len(words) > 0:
            root["values"].append({"key": "words", "values": words})
            return root

        for index in range(start_index + 1, len(cues)):
            c_level, c_title, c_words, _ = cues[index]
            if c_level > level:
                t = _create_tree(index)
                if t:
                    root["values"].append(t)
            elif c_level <= level:
                return root

        return root

    return _create_tree(0)


def markdown_to_yml(filepath: Path, stream_out: TextIO):
    with open(filepath, "r") as f:
        s = f.read()

    T = create_tree(s)
    yaml.dump(T, sys.stdout, allow_unicode=True)


def __markdown_to_yml__(list_markdown_filepath: List[str], *args, **kwargs):
    """
    Convert markdown categorized file to yml.

    Given a list of words hierarchicaly categorized in markdown format,
    convert it to yaml.
    """

    for filepath in list_markdown_filepath:
        markdown_to_yml(filepath, sys.stdout)


def extend_parser(subparser_action=None):
    command_name = "markdown-to-yml"
    description = __markdown_to_yml__.__doc__
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
