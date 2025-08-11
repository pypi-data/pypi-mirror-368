from vibetrimleft import vibetrimleft
from dotenv import load_dotenv

load_dotenv()


def test_vibetrimleft():
    assert vibetrimleft("   hello world") == "hello world"
    assert vibetrimleft("    test") == "test"
    assert vibetrimleft("   spaces on right   ") == "spaces on right   "
    assert vibetrimleft("no leading") == "no leading"


def test_only_whitespace():
    assert vibetrimleft("   ") == ""
    assert vibetrimleft("\t\t") == ""
    assert vibetrimleft("\n\n") == ""


def test_mixed_whitespace():
    assert vibetrimleft(" \t\n hello") == "hello"
    assert vibetrimleft("\t  \ntext") == "text"
    assert vibetrimleft("  \tleading and trailing  \t") == "leading and trailing \t"


def test_empty_string():
    assert vibetrimleft("") == ""


def test_newlines_and_tabs():
    assert vibetrimleft("\n\nline1\nline2") == "line1\nline2"
    assert vibetrimleft("\t\t\ttabbed") == "tabbed"


def test_preserves_internal_whitespace():
    assert vibetrimleft("  hello   world  ") == "hello   world  "
    assert vibetrimleft("\tspaced\ttext\t") == "spaced\ttext\t"