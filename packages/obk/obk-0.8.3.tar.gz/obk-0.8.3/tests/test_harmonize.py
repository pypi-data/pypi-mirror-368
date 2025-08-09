import obk.harmonize as harmonize


def test_harmonize_text_code_blocks_and_tags():
    text = (
        "start\n"  # normal
        "```\n"  # enter code block
        "<tag>inside</tag>\n"  # inside code block
        "```\n"  # exit code block
        "<gsl-purpose>\nline\n"
    )
    result, actions = harmonize.harmonize_text(text)
    assert "inside" in result
    assert any("Inserted blank" in a for a in actions)
