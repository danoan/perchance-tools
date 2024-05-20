from danoan.perchance_tools.core import api, model

import io

markdown_text = """
# Characters
## Age
### Adjective
baby
kid
old
young
"""


def test_markdown_to_yml():
    ss = io.StringIO()
    ss.write(markdown_text)
    ss.seek(0, io.SEEK_SET)

    d = api.create_dict_from_markdown(ss)
    assert d["root"]["Characters"]["Age"]["Adjective"]["words"].extract() == [
        "baby",
        "kid",
        "old",
        "young",
    ]


def test_correct_word():
    ss = io.StringIO()
    ss.write(markdown_text)
    ss.seek(0, io.SEEK_SET)

    d = api.create_dict_from_markdown(ss)

    ci = model.CorrectionInstructions(
        ["root", "Characters", "Age", "Adjective"],
        [("baby", "bebe"), ("kid", "enfant")],
    )

    cd = api.correct_words(d, [ci])
    assert cd["root"]["Characters"]["Age"]["Adjective"]["words"].extract() == [
        "bebe",
        "enfant",
        "old",
        "young",
    ]
