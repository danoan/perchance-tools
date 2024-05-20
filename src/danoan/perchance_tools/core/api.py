from hashlib import sha256
from pathlib import Path
from danoan.perchance_tools.core import model, utils
from danoan.llm_assistant.core import api as llm_assistant

from importlib import resources
from jinja2 import Template
import json
import logging
import sys
import re
from typing import Any, Dict, List, TextIO

LOG_LEVEL = logging.DEBUG

logger = logging.getLogger(__file__)
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(LOG_LEVEL)
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)

# -------------------- Markdown to YML --------------------


def _collect_markdown_markers(markdown_text: str):
    """
    Return the start and end characters of header titles in a markdown.

    >>> markdown_text = '''
    ... # Running journal
    ... This document register my running trainings.
    ... ## 1st April 2024
    ... Ran 5km in 30 minutes.
    ... '''
    >>> markers = list(_collect_markdown_markers(markdown_text))
    >>> assert( markers[0] == (1,'Running journal', (1,18)))
    >>> assert( markers[1] == (2,'1st April 2024', (64,81)))
    """
    header_start = re.compile(r"^[ ]*(#+)\s*([^\n]*)", re.MULTILINE)

    for m in header_start.finditer(markdown_text):
        header_marker, header_title = m.groups()
        header_level = len(header_marker)
        yield (header_level, header_title, m.span())


def _parse_markdown(markdown_text: str):
    """
    Parse markdown text into (level, title, list of words) components.
    """
    m = list(_collect_markdown_markers(markdown_text))
    m.append((0, 0, (len(markdown_text), len(markdown_text))))

    for e, n in zip(m[:-1], m[1:]):
        level, title, span = e
        _, _, next_span = n

        start, end = span
        next_start, _ = next_span

        words = set()
        for w in markdown_text[end:next_start].split("\n"):
            _w = w.strip()
            if len(_w) == 0:
                continue
            words.add(_w)

        yield ([level, title, list(sorted(words)), False])


def create_dict_from_markdown(markdown_stream: TextIO) -> model.WordDict:
    """
    Create a dictionary from markdown text.

    Header titles are mapped to keys which its value
    is a list of dictionaries created from its sub-headers.

    Each line of a non-header text is included as an item in a
    list which itself is contained in a dictionary with a unique
    key named "words".
    """
    cues = [[0, "root", [], False]]
    cues.extend(list(_parse_markdown(markdown_stream.read())))

    def _create_tree(start_index: int):
        level, title, words, visited = cues[start_index]
        if visited:
            return None

        cues[start_index][3] = True
        root = {title.strip(): []}
        if len(words) > 0:
            root[title.strip()] = [{"words": words}]
            return root

        for index in range(start_index + 1, len(cues)):
            c_level, c_title, c_words, _ = cues[index]
            if c_level > level:
                t = _create_tree(index)
                if t:
                    root[title.strip()].append(t)
            elif c_level <= level:
                return root

        return root

    return model.WordDict(_create_tree(0))


# -------------------- Correct Words --------------------


def correct_words(
    word_dict: model.WordDict,
    correction_instructions: List[model.CorrectionInstructions],
):
    for instruction in correction_instructions:
        u = word_dict
        for category in instruction.categories:
            u = u[category]

        set_of_words = set(u["words"].extract())
        for correction_pair in instruction.corrections:
            original, correction = correction_pair
            set_of_words.remove(original)
            set_of_words.add(correction)

        u["words"] = list(sorted(set_of_words))

    return word_dict


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


def _singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@_singleton
class _Cache:
    def __init__(self):
        # self.cache_folder = Path(__file__).parent / "llm-cache"
        self.cache_folder = Path("/home/daniel/Projects/Git/perchance-tools/llm-cache")
        self.cache_folder.mkdir(parents=True, exist_ok=True)

    def load(self, prompt: llm_assistant.model.PromptConfiguration):
        m = f"{prompt.system_prompt}-{prompt.user_prompt}"
        k = sha256(m.encode("utf-8")).hexdigest()
        cache_file = self.cache_folder / f"{k}.txt"
        if cache_file.exists():
            with open(cache_file, "r") as f:
                return f.read()
        else:
            return None

    def save(self, prompt: llm_assistant.model.PromptConfiguration, response: str):
        m = f"{prompt.system_prompt}-{prompt.user_prompt}"
        k = sha256(m.encode("utf-8")).hexdigest()
        cache_file = self.cache_folder / f"{k}.txt"
        with open(cache_file, "w") as f:
            f.write(response)


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

    cache = _Cache()
    result = cache.load(prompt)
    if not result:
        result = llm_assistant.custom(prompt, model=model, **data)
        cache.save(prompt, result.content)

    return cache.load(prompt)


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
            correction["categories"] = categories
            correction["corrections"] = json.loads(r)

            if correction["corrections"] and len(correction["corrections"]) > 0:
                logger.debug(categories)
                logger.debug(correction["corrections"])

        except json.JSONDecodeError as ex:
            logger.debug("Error decoding LLM response as json")
            logger.debug(categories)
            logger.debug(r)
            # If an error is found while generating the JSON, I assume the list of
            # corrections is empty
            correction["corrections"] = []

        yield correction


def find_corrections(
    word_dict: model.WordDict, language
) -> List[model.CorrectionInstructions]:
    return [
        model.CorrectionInstructions(**x)
        for x in _find_corrections(word_dict, language, "gpt-4o")
    ]
