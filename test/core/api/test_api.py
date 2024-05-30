from danoan.perchance_tools.core import api, model

import io
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


def test_correct_word():
    input_file = ASSETS_FOLDER / "correct_words" / "in_markdown_thesaurus.md"
    expected_file = ASSETS_FOLDER / "correct_words" / "ex_markdown_thesaurus.md"

    with open(input_file, "r") as f_in, open(expected_file, "r") as f_ex:
        d = api.create_dict_from_markdown(f_in)

        ci = model.CorrectionInstructions(
            ["root", "Personnages", "Age", "Adjectifs"],
            [("baby", "bebe"), ("kid", "enfant")],
        )

        cd = api.correct_words(d, [ci])
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
