from h2m2t.h2m import html_to_markdown
from h2m2t.m2t import markdown_to_text


def html_to_text(
    html: str,
    parser: str = "html.parser",
    *,
    strip_tags: list | None = None,
) -> str:
    md = html_to_markdown(html, parser, strip_tags=strip_tags)
    txt = markdown_to_text(md)

    return txt.strip()
