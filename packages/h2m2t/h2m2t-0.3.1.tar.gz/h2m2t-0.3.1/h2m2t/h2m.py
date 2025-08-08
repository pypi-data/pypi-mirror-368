import re

from bs4 import BeautifulSoup

from h2m2t.html import fix_html_tree
from h2m2t.markdown import MarkdownConverterFixed


def html_to_markdown(
    html: str,
    parser: str = "html.parser",
    *,
    strip_tags: list | None = None,
) -> str:
    soup = BeautifulSoup(html, parser)
    fix_html_tree(soup)

    converter = MarkdownConverterFixed(strip=strip_tags, autolinks=False, heading_style="atx")
    md = converter.convert_soup(soup)
    md = f"\n{md}\n"

    # Fix spaces after inline elements splitting
    md = re.sub("\u00a0{2,}", "\u00a0", md, flags=re.UNICODE)
    md = md.replace(" \u00a0", " ").replace("\u00a0 ", " ")
    md = md.replace("\u00a0\n", "\n").replace("\n\u00a0", "\n")

    # Clean newlines
    md = re.sub(r"\n[^\S\n]+\n", "\n\n", md, flags=re.UNICODE)
    md = re.sub(r"\n[^\S\n]+\n", "\n\n", md, flags=re.UNICODE)
    md = re.sub(r"\n{3,}", "\n\n", md)

    return md.strip()
