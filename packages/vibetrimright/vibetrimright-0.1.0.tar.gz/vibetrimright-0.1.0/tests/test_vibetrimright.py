from vibetrimright import vibetrimright
from dotenv import load_dotenv

load_dotenv()


def test_vibetrimright():
    assert vibetrimright("hello world   ") == "hello world"
    assert vibetrimright("test    ") == "test"
    assert vibetrimright("   spaces on left   ") == "   spaces on left"
    assert vibetrimright("no trailing") == "no trailing"


def test_only_whitespace():
    assert vibetrimright("   ") == ""
    assert vibetrimright("\t\t") == ""
    assert vibetrimright("\n\n") == ""


def test_mixed_whitespace():
    assert vibetrimright("hello \t\n ") == "hello"
    assert vibetrimright("text\t  \n") == "text"
    assert vibetrimright("  leading and trailing  \t") == "  leading and trailing"


def test_empty_string():
    assert vibetrimright("") == ""


def test_newlines_and_tabs():
    assert vibetrimright("line1\nline2\n\n") == "line1\nline2\n"
    assert vibetrimright("tabbed\t\t\t") == "tabbed"