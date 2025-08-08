import re
from collections.abc import Callable

from bs4 import Tag
from markdownify import MarkdownConverter
from mistune import HTMLRenderer

from h2m2t.text import replace_rare_spaces


class HTMLRendererFixed(HTMLRenderer):
    def link(self, text: str, url: str, title: str | None = None) -> str:
        url = url.replace("%20", " ")
        url = url.replace("%28", "(").replace("%29", ")")
        return super().link(text, url, title)


class MarkdownConverterFixed(MarkdownConverter):
    root_tags = (
        "a",
        "b",
        "blockquote",
        "code",
        "pre",
        "del",
        "em",
        "kbd",
        "dd",
        "dl",
        "dt",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "i",
        "ul",
        "ol",
        "table",
        "s",
        "strong",
        "samp",
        "sub",
        "sup",
    )

    def process_text(self, el: Tag, parent_tags: set[str] | None = None) -> str:
        text = super().process_text(el, parent_tags)

        if "code" not in parent_tags and "pre" not in parent_tags:
            text = text.replace("<", "\\<").replace(">", "\\>")

        if set(self.root_tags).intersection(parent_tags):
            return text

        for b in self.options["bullets"]:
            if text.rstrip() == b or text.startswith(f"{b} "):
                text = f"\\{text}"

        if m := re.match(r"\d+\. ", text):
            number, text = text[: m.end() - 2], text[m.end() :]
            text = rf"{number}\. {text}"

        return text

    def get_conv_fn(self, tag_name: str) -> Callable[[Tag, str, set[str]], str]:
        conv_fn = super().get_conv_fn(tag_name)

        def _conv_fn(el: Tag, text: str, parent_tags: set[str]) -> str:
            text = replace_rare_spaces(text)
            return conv_fn(el, text, parent_tags)

        return conv_fn if conv_fn is None else _conv_fn

    def _convert_hn(self, n: int, el: Tag, text: str, parent_tags: set[str]) -> str:
        if not text.strip():
            return "\n"

        text = re.sub("\n+", "\t", text).strip()

        if "_inline" not in parent_tags and set(self.root_tags).intersection(parent_tags):
            return "\n\n" + self.convert_b(el, text, parent_tags).strip() + "\n\n"

        return super()._convert_hn(n, el, text, parent_tags)

    def convert_pre(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        text = text.strip("\n")

        return super().convert_pre(el, text, parent_tags)

    def convert_code(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        text = text.strip("\n")

        return super().convert_code(el, text, parent_tags)

    def convert_img(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        self.strip_attr(el, "alt")
        self.strip_attr(el, "title")
        self.strip_attr(el, "src")
        self.strip_attr(el, "data-original")

        alt = el.attrs["alt"]
        title = el.attrs["title"]
        src = el.attrs["src"]
        original = el.attrs["data-original"]

        if not src and original:
            el.attrs["src"] = src = original

        if not alt and not title and not src:
            return ""

        return super().convert_img(el, text, parent_tags)

    def convert_video(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        self.strip_attr(el, "src")
        self.strip_attr(el, "poster")

        return super().convert_video(el, text, parent_tags)

    def convert_a(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        self.strip_attr(el, "title")
        self.strip_attr(el, "href")

        href = el.attrs["href"].replace(" ", "%20")
        href = href.replace("(", "%28").replace(")", "%29")
        el.attrs["href"] = href

        text = re.sub("\n+", "\t", text).strip()

        return super().convert_a(el, text, parent_tags)

    def convert_option(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        return super().convert_div(el, text, parent_tags)

    @staticmethod
    def strip_attr(el: Tag, attr: str) -> None:
        value = el.attrs.get(attr, None) or ""
        value = replace_rare_spaces(value)
        value = re.sub("\n+", "\t", value)
        el.attrs[attr] = value.strip()
