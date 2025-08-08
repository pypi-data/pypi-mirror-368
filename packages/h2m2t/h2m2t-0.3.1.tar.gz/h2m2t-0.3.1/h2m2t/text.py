import re
from html import unescape

from ftfy import fix_text

whitespace_chars = [
    # "\u0009",
    # "\u000a",
    # "\u000b",
    # "\u000c",
    # "\u000d",
    # "\u0020",
    # "\u0085",
    # "\u00a0",
    # "\u1680",
    # "\u2000",
    # "\u2001",
    # "\u2002",
    # "\u2003",
    # "\u2004",
    # "\u2005",
    # "\u2006",
    # "\u2007",
    # "\u2008",
    # "\u2009",
    # "\u200a",
    "\u200b",
    "\u200c",
    "\u200d",
    # "\u2028",
    # "\u2029",
    # "\u202f",
    # "\u205f",
    "\u2060",
    # "\u3000",
]


def repair_html_entities(text: str) -> str:
    before = ""

    while text != before:
        before, text = text, unescape(text)

    return text


def repair_broken_unicode(text: str) -> str:
    return fix_text(text, normalization="NFKD")


def replace_rare_spaces(text: str) -> str:
    spaces = "".join(whitespace_chars)

    return re.sub(f"[{spaces}]", " ", text, flags=re.UNICODE)
