from danoan.perchance_tools.core import api, model
from danoan.llm_assistant.core import api as llm_assistant
from danoan.llm_assistant.core.model import LLMAssistantConfiguration

import pytest

import io
import pycountry
from pathlib import Path
import yaml

SCRIPT_FOLDER = Path(__file__).parent
ASSETS_FOLDER = SCRIPT_FOLDER / "assets"


def test_markdown_to_yml():
    input_file = ASSETS_FOLDER / "markdown_to_yml" / "in_markdown_thesaurus.md"
    expected_file = ASSETS_FOLDER / "markdown_to_yml" / "ex_markdown_thesaurus.yml"

    with open(input_file, "r") as f_in, open(expected_file, "r") as f_ex:
        d = api.create_dict_from_markdown(f_in)

        assert d["root"]["Personnages"]["Sexe"]["Adjectifs"]["words"].extract() == [
            "féminin",
            "masculin",
        ]

        ss = io.StringIO()
        yaml.dump(d.extract(), ss)
        ss.seek(0, io.SEEK_SET)

        code_generated_yaml = yaml.load(ss, Loader=yaml.Loader)
        expected_yaml = yaml.load(f_ex, Loader=yaml.Loader)

        assert code_generated_yaml == expected_yaml


def test_replace_words():
    input_file = ASSETS_FOLDER / "replace_words" / "in_markdown_thesaurus.md"
    expected_file = ASSETS_FOLDER / "replace_words" / "ex_markdown_thesaurus.md"

    with open(input_file, "r") as f_in, open(expected_file, "r") as f_ex:
        d = api.create_dict_from_markdown(f_in)

        ci = model.ReplaceInstructions(
            ["root", "Personnages", "Age", "Adjectifs"],
            [("baby", "bebe"), ("kid", "enfant")],
        )

        cd = api.replace_words(d, [ci])
        assert cd["root"]["Personnages"]["Age"]["Adjectifs"]["words"].extract() == [
            "avancé",
            "bebe",
            "croulant",
            "enfant",
            "entre deux ages",
            "frais",
            "old",
            "young",
        ]


def test_find_corrections(openai_key):
    cache_path = SCRIPT_FOLDER / "cache" / ".cache"
    config = LLMAssistantConfiguration(openai_key, True, cache_path)
    llm_assistant.LLMAssistant().setup(config)

    input_file = ASSETS_FOLDER / "replace_words" / "in_markdown_thesaurus.md"

    expected_replace_instructions = [
        model.ReplaceInstructions(
            key=["root", "Personnages", "Sexe", "Adjectifs"], replace_pairs=[]
        ),
        model.ReplaceInstructions(
            key=["root", "Personnages", "Sexe", "Noms"], replace_pairs=[]
        ),
        model.ReplaceInstructions(
            key=["root", "Personnages", "Age", "Adjectifs"],
            replace_pairs=[["entre deux ages", "entre deux âges"]],
        ),
    ]

    with open(input_file, "r") as f_in:
        d = api.create_dict_from_markdown(f_in)
        replace_instructions = api.find_corrections(
            d, pycountry.languages.get(name="French")
        )

        assert replace_instructions == expected_replace_instructions


@pytest.mark.parametrize(
    "word,from_language,to_language,expected",
    [
        ("chair", "english", "french", ["chaise", "fauteuil", "siège"]),
        (
            "badiner",
            "french",
            "english",
            ["to joke", "to jest", "to banter", "to fool around"],
        ),
    ],
)
def test_translation(
    openai_key: str, word: str, from_language: str, to_language: str, expected: str
):
    cache_path = SCRIPT_FOLDER / "cache" / ".cache"
    config = LLMAssistantConfiguration(openai_key, True, cache_path)
    llm_assistant.LLMAssistant().setup(config)

    assert api.translate(word, from_language, to_language) == expected
