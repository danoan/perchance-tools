from danoan.perchance_tools.core import model, utils


def test_collect_key_path():
    d = {
        "root": {
            "Category_A": {
                "Category_B1": {"words": ["word_a", "word_b", "word_c"]},
                "Category_B2": {"words": ["word_d", "word_e"]},
            }
        }
    }
    w = model.WordDict(d)
    L = list(utils.collect_key_path(w, "words"))
    assert L[0]["path"] == ["root", "Category_A", "Category_B1"]
    assert L[0]["words"] == ["word_a", "word_b", "word_c"]
