from mistune import create_markdown

from h2m2t.markdown import HTMLRendererFixed


def markdown_to_html(md: str) -> str:
    renderer = HTMLRendererFixed(escape=False, allow_harmful_protocols=True)
    markdown = create_markdown(
        renderer=renderer,
        plugins=[
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
        ],
    )

    markdown.block.rules.remove("setex_heading")
    markdown.block.block_quote_rules.remove("setex_heading")
    markdown.block.list_rules.remove("setex_heading")

    html = markdown(md)

    return f'<!doctype html><html><head><meta charset="utf-8"><title></title></head><body>{html}</body></html>'
