from danoan.perchance_tools.core import exception, model, utils
from danoan.llm_assistant.core import api as llm_assistant

from dataclasses import dataclass
from importlib import resources
from jinja2 import Template
import json
import logging
from pathlib import Path
import sys
import re
from typing import Any, Dict, Generator, List, TextIO, Tuple

LOG_LEVEL = logging.DEBUG

logger = logging.getLogger(__file__)
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(LOG_LEVEL)
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)

# -------------------- Markdown to YML --------------------


@dataclass
class MarkdownMarker:
    level: int
    title: str
    character_span: Tuple[int, int]


@dataclass
class MarkdownCue:
    level: int
    title: str
    lines: List[str]


def _collect_markdown_markers(
    markdown_text: str,
) -> Generator[MarkdownMarker, None, None]:
    """
    Return the start and end characters of header titles in a markdown.

    >>> markdown_text = '''
    ... # Running journal
    ... This document register my running trainings.
    ... ## 1st April 2024
    ... Ran 5km in 30 minutes.
    ... '''
    >>> markers = list(_collect_markdown_markers(markdown_text))
    >>> m0 = markers[0]
    >>> m1 = markers[1]
    >>> assert( (m0.level,m0.title,m0.character_span) == (1,'Running journal', (1,18)))
    >>> assert( (m1.level,m1.title,m1.character_span) == (2,'1st April 2024', (64,81)))
    """
    header_start = re.compile(r"^[ ]*(#+)\s*([^\n]*)", re.MULTILINE)

    for m in header_start.finditer(markdown_text):
        header_marker, header_title = m.groups()
        header_level = len(header_marker)
        yield MarkdownMarker(header_level, header_title, m.span())


def _parse_markdown(markdown_text: str) -> Generator[MarkdownCue, None, None]:
    """
    Parse markdown text into (level, title, list of words) components.
    """
    m = list(_collect_markdown_markers(markdown_text))
    m.append(MarkdownMarker(0, "root", (len(markdown_text), len(markdown_text))))

    for e, n in zip(m[:-1], m[1:]):
        level, title, span = e.level, e.title, e.character_span
        next_span = n.character_span

        start, end = span
        next_start, _ = next_span

        words = set()
        for w in markdown_text[end:next_start].split("\n"):
            _w = w.strip()
            if len(_w) == 0:
                continue
            words.add(_w)

        yield MarkdownCue(level, title, list(sorted(words)))


def create_dict_from_markdown(markdown_stream: TextIO) -> model.WordDict:
    """
    Create a dictionary from markdown text.

    Header titles are mapped to keys which values
    are dictionaries themselves created from theirs sub-headers.

    The text level is stored in the key `words` within its
    closest header-level dictionary. The `words` key stores the
    lines of the text.
    """
    cues = [MarkdownCue(0, "root", [])]
    cues.extend(list(_parse_markdown(markdown_stream.read())))
    visited = [False] * len(cues)

    def _create_tree(start_index: int):
        mc = cues[start_index]
        if visited[start_index]:
            return None

        visited[start_index] = True
        root: Dict[str, Any] = {mc.title.strip(): {}}
        if len(mc.lines) > 0:
            root[mc.title.strip()] = {"words": mc.lines}
            return root

        for index in range(start_index + 1, len(cues)):
            c = cues[index]
            if c.level > mc.level:
                t = _create_tree(index)
                if t:
                    root[mc.title.strip()].update(t)
            elif c.level <= mc.level:
                return root

        return root

    return model.WordDict(_create_tree(0))


# -------------------- Correct Words --------------------


def _get_asset(asset_relative_path: Path):
    ASSETS_PACKAGE = "danoan.perchance_tools.assets"

    s = []
    t = asset_relative_path
    while t != t.parent:
        s.append(t.name)
        t = t.parent
    s.reverse()

    asset_dot_path = ".".join(s[:-1])
    resource_dot_path = f"{ASSETS_PACKAGE}.{asset_dot_path}"
    return resources.path(resource_dot_path, s[-1])


def _read_asset_as_text(asset_relative_path: Path):
    asset_path = _get_asset(asset_relative_path)
    with open(asset_path, "r") as f:
        return f.read()


def _setup_llm_assistant():
    instance = llm_assistant.LLMAssistant()
    if not instance.config:
        config = llm_assistant.get_configuration()
        if not config.use_cache:
            raise exception.CacheNotConfiguredError()

        instance.setup(config)


def _render_correct_words_user_prompt(categories: List[str], words: List[str]):
    template_data = _read_asset_as_text(
        Path("prompts") / "correct_words" / "user.txt.tpl"
    )
    template = Template(template_data)

    return template.render(categories=categories, words=words)


def _call_correct_word_prompt(user_prompt: str, language, model: str):
    system_prompt = _read_asset_as_text(
        Path("prompts") / "correct_words" / "system.txt.tpl"
    )
    full_examples = _read_asset_as_text(
        Path("prompts") / "correct_words" / language.alpha_3 / "full-examples.txt"
    )

    data = {
        "language": language.name,
        "full_examples": full_examples,
    }

    prompt = llm_assistant.model.PromptConfiguration(
        "correct-words", system_prompt, user_prompt
    )

    _setup_llm_assistant()
    result = llm_assistant.custom(prompt, model=model, **data)

    return result.content


def _ensure_json_list_string(text_response: str):
    response_lines = text_response.splitlines()
    first_line = 0
    for i, line in enumerate(response_lines):
        if line and line[0] == "[":
            first_line = i
            break
    return "".join(response_lines[first_line:])


def _find_corrections(word_dict: model.WordDict, language, model: str):
    for key_path in utils.collect_key_path(word_dict, "words"):
        categories = key_path["path"]
        render_categories = [x for x in categories]
        render_categories.remove("root")
        words = key_path["words"]

        user_prompt = _render_correct_words_user_prompt(render_categories, words)
        r = _call_correct_word_prompt(user_prompt, language, model)
        r = _ensure_json_list_string(r)

        try:
            correction = {}
            correction["key"] = categories
            correction["replace_pairs"] = json.loads(r)

            if correction["replace_pairs"] and len(correction["replace_pairs"]) > 0:
                logger.debug(categories)
                logger.debug(correction["replace_pairs"])

        except json.JSONDecodeError as ex:
            logger.debug("Error decoding LLM response as json")
            logger.debug(categories)
            logger.debug(r)
            logger.debug(ex)
            # If an error is found while generating the JSON, I assume the list of
            # corrections is empty
            correction["replace_pairs"] = []

        yield correction


def replace_words(
    word_dict: model.WordDict,
    correction_instructions: List[model.ReplaceInstructions],
):
    """
    Executes a series of replace operations in a WordDict.

    The CorrectionInstruction has a key and a list of replace
    pairs with old and new word.
    """
    for instruction in correction_instructions:
        u = word_dict
        for category in instruction.key:
            u = u[category]

        set_of_words = set(u["words"].extract())
        for correction_pair in instruction.replace_pairs:
            original, correction = correction_pair
            set_of_words.remove(original)
            set_of_words.add(correction)

        u["words"] = list(sorted(set_of_words))

    return word_dict


def find_corrections(
    word_dict: model.WordDict, language
) -> List[model.ReplaceInstructions]:
    return [
        model.ReplaceInstructions(**x)
        for x in _find_corrections(word_dict, language, "gpt-4o")
    ]


# -------------------- Perchance format --------------------


def translate(word: str, from_language: str, to_language: str) -> List[str]:
    system_prompt_template = _read_asset_as_text(
        Path("prompts") / "translate" / "system.txt.tpl"
    )
    user_prompt_template = _read_asset_as_text(
        Path("prompts") / "translate" / "user.txt.tpl"
    )
    data = {
        "word": word,
        "from_language_name": from_language,
        "to_language_name": to_language,
    }

    system_prompt = Template(system_prompt_template).render(**data)
    user_prompt = Template(user_prompt_template).render(**data)

    prompt = llm_assistant.model.PromptConfiguration(
        "translate-word", system_prompt, user_prompt
    )

    _setup_llm_assistant()
    result = llm_assistant.custom(prompt, model="gpt-3.5-turbo")
    response = result.content

    if not response:
        return []
    else:
        try:
            response_data = json.loads(response)
            if type(response_data) is list:
                return response_data
            else:
                logger.debug("Expected a list")
                raise TypeError()
        except json.JSONDecodeError:
            logger.debug("Error decoding LLM response as json")
            logger.debug(word)
            return [word]
