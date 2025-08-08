import re
from typing import Any, ClassVar, Literal

from bs4 import BeautifulSoup
from mistune import BaseRenderer, BlockState, InlineParser, Markdown, import_plugin


def markdown_to_text(md: str, parser: str = "html.parser") -> str:
    plugins = [
        # Default:
        "strikethrough",
        "footnotes",
        "table",
        "speedup",
        # Enabled:
        "url",
        "task_lists",
        "def_list",
        "abbr",
        "mark",
        "insert",
        "superscript",
        "subscript",
        "math",
        # "ruby",
        "spoiler",
    ]

    inline = InlineParser(hard_wrap=False)
    real_plugins = [import_plugin(n) for n in plugins]
    markdown = Markdown(renderer=TextRenderer(parser), inline=inline, plugins=real_plugins)

    text = markdown(md)

    text = re.sub(r"[^\S\n]*\n[^\S\n]*", "\n", text, flags=re.UNICODE)
    text = re.sub("([^\\S\n])[^\\S\n]+", " ", text, flags=re.UNICODE)
    text = re.sub("\n{3,}", "\n\n", text)

    return text.strip()


class TextRenderer(BaseRenderer):
    """A renderer for converting Markdown to Text."""

    NAME: ClassVar[Literal["text"]] = "text"

    def __init__(self, parser: str = "html.parser") -> None:
        super().__init__()
        self._html_parser = parser

    def render_token(self, token: dict[str, Any], state: BlockState) -> str:
        # backward compitable with v2
        func = self._get_method(token["type"])
        attrs = token.get("attrs")

        if "raw" in token:
            text = token["raw"]
        elif "children" in token:
            text = self.render_tokens(token["children"], state)
        elif attrs:
            return func(**attrs)
        else:
            return func()
        if attrs:
            return func(text, **attrs)
        return func(text)

    def text(self, text: str) -> str:
        return text

    def emphasis(self, text: str) -> str:
        return text

    def strong(self, text: str) -> str:
        return text

    def link(self, text: str, url: str, title: str | None = None) -> str:
        if title and title != text:
            return f"{text} [{title}]"

        return text

    def image(self, text: str, url: str, title: str | None = None) -> str:
        if title and title != text:
            return f"{text} [{title}]"

        return text

    def codespan(self, text: str) -> str:
        return text

    def linebreak(self) -> str:
        return "\n"

    def softbreak(self) -> str:
        return "\n"

    def inline_html(self, html: str) -> str:
        return BeautifulSoup(html, self._html_parser).get_text(separator=" ")

    def paragraph(self, text: str) -> str:
        return f"\n\n{text}\n\n"

    def heading(self, text: str, level: int, **attrs: Any) -> str:
        return f"\n\n{text}\n\n"

    def blank_line(self) -> str:
        return "\n"

    def thematic_break(self) -> str:
        return "\n"

    def block_text(self, text: str) -> str:
        return f"\n\n{text}\n\n"

    def block_code(self, code: str, info: str | None = None) -> str:
        return f"\n\n{code}\n\n"

    def block_quote(self, text: str) -> str:
        return f"\n\n{text}\n\n"

    def block_html(self, html: str) -> str:
        text = BeautifulSoup(html, self._html_parser).get_text(separator=" ")
        return f"\n\n{text.strip()}\n\n"

    def block_error(self, text: str) -> str:
        return f"\n\n{text}\n\n"

    def list(self, text: str, ordered: bool, **attrs: Any) -> str:
        return f"\n\n{text}\n\n"

    def list_item(self, text: str) -> str:
        return f"{text.strip()}\n"

    # strikethrough
    def strikethrough(self, text: str) -> str:
        return text

    # footnotes
    def footnote_ref(self, key: str, index: int) -> str:
        return ""

    def footnote_item(self, text: str, index: int) -> str:
        return f"{text.strip()}\n"

    def footnotes(self, text: str) -> str:
        return f"\n\n{text}\n\n"

    # table
    def table(self, text: str) -> str:
        return f"\n\n{text}\n\n"

    def table_head(self, text: str) -> str:
        return f"\n{text}\n"

    def table_body(self, text: str) -> str:
        return f"\n{text}\n"

    def table_row(self, text: str) -> str:
        return f"{text}\n"

    def table_cell(self, text: str, align: str | None = None, head: bool = False) -> str:
        return f"\t{text.strip()}\t"

    # - speedup

    # - url

    # task_lists
    def task_list_item(self, text: str) -> str:
        return f"{text.strip()}\n"

    # def_list
    def def_list(self, text: str) -> str:
        return f"\n\n{text}\n\n"

    def def_list_head(self, text: str) -> str:
        return f"{text.strip()}\n"

    def def_list_item(self, text: str) -> str:
        return f"{text.strip()}\n"

    # abbr
    def abbr(self, text: str, title: str) -> str:
        if title and title != text:
            return f"{text} [{title}]"

        return text

    # mark
    def mark(self, text: str) -> str:
        return text

    # insert
    def insert(self, text: str) -> str:
        return text

    # superscript
    def superscript(self, text: str) -> str:
        return text

    # subscript
    def subscript(self, text: str) -> str:
        return text

    # math
    def block_math(self, text: str) -> str:
        return f"\n\n{text}\n\n"

    def inline_math(self, text: str) -> str:
        return text

    # spoiler
    def block_spoiler(self, text: str) -> str:
        return f"\n\n{text}\n\n"

    def inline_spoiler(self, text: str) -> str:
        return text
