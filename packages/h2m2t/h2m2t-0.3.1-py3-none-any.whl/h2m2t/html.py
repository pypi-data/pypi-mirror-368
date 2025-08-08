from bs4 import BeautifulSoup, Comment, NavigableString, PageElement, Tag

from h2m2t.table import tables_to_dense
from h2m2t.text import replace_rare_spaces

meaningless_tags = [
    "air",  # vc.ru
    "air-settings",  # vc.ru
    "applet",
    "audio",
    "canvas",
    "embed",
    "frame",
    "frameset",
    "head",
    "iframe",
    "link",
    "map",
    "meta",
    "noembed",
    "noframes",
    "noscript",
    "object",
    "plaintext",
    "script",
    "style",
    "svg",
    "template",
    "title",
    "video",
    "xmp",
]

block_tags = [
    "address",
    "article",
    "aside",
    "blockquote",
    "br",  # inline, but behaves as block
    "canvas",
    # "dd",  # child
    "div",
    "dl",
    # "dt",  # child
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "legend",
    "li",  # child
    "main",
    "nav",
    "noscript",
    "ol",
    "optgroup",  # child
    "option",  # child
    "pre",
    "section",
    "table",
    "tbody",  # child
    "td",  # child
    "tfoot",  # child
    "th",  # child
    "thead",  # child
    "tr",  # child
    "ul",
    "video",
]

inline_tags = [
    "a",
    "abbr",
    "acronym",
    "b",
    "bdo",
    "big",
    "button",
    # "br",  # inline, but behaves as block
    "cite",
    "code",
    "dfn",
    "em",
    "i",
    "img",
    "input",
    "kbd",
    "label",
    "map",
    "object",
    "output",
    "q",
    "s",
    "samp",
    "script",
    "select",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "textarea",
    "time",
    "tt",
    "u",
    "var",
]

child_tags = [
    "dd",  # child
    "dt",  # child
    "li",  # child
    "optgroup",  # child
    "option",  # child
    "tbody",  # child
    "td",  # child
    "tfoot",  # child
    "th",  # child
    "thead",  # child
    "tr",  # child
]


def fix_html_tree(soup: BeautifulSoup) -> None:
    _drop_meaningless(soup)
    _unwrap_nested_tables(soup)
    _fix_spaces(soup)
    _fix_newlines(soup)
    _fix_inline(soup)
    _fix_block(soup)
    tables_to_dense(soup, deduplicate=True, unwrap=True)


def _drop_meaningless(soup: BeautifulSoup) -> None:
    # Drop non-meaning tags
    for node in soup(meaningless_tags):
        _merge_siblings(node)
        node.decompose()

    # Drop comments
    for comment in soup(string=lambda s: isinstance(s, Comment)):
        _merge_siblings(comment)
        comment.decompose()


def _unwrap_nested_tables(soup: BeautifulSoup) -> None:
    for table in soup("table"):
        if not table("table"):
            continue

        nodes = [table]
        for body in table(["thead", "tbody", "tfoot"], recursive=False):
            nodes.append(body)
            for row in body("tr", recursive=False):
                nodes.append(row)
                nodes.extend(row(["td", "th"], recursive=False))
        for row in table("tr", recursive=False):
            nodes.append(row)
            nodes.extend(row(["td", "th"], recursive=False))

        for node in nodes:
            node.name = "div"


def _fix_spaces(soup: BeautifulSoup) -> None:
    # Move spaces out from inline elements
    for node in soup(inline_tags):
        _fix_inline_spaces(node)


def _fix_inline_spaces(node: Tag) -> None:
    if node.contents:
        _fix_spaces_left(node, node.contents[0])
    if node.contents:
        _fix_spaces_right(node, node.contents[-1])

    if node.parent and node.parent.name in inline_tags:
        _fix_inline_spaces(node.parent)


def _fix_spaces_left(node: Tag, element: PageElement) -> None:
    if not isinstance(element, NavigableString):
        return

    body = str(element).lstrip()
    if str(element) == body:
        return

    if not body:
        node.insert_after(NavigableString(str(element)))
        element.decompose()
        return

    head = str(element).split(body)[0]
    before = node.previous_sibling
    if isinstance(before, NavigableString):
        string = str(before) + head
        before.replace_with(NavigableString(string))
    else:
        node.insert_before(NavigableString(head))

    element.replace_with(NavigableString(body))


def _fix_spaces_right(node: Tag, element: PageElement) -> None:
    if not isinstance(element, NavigableString):
        return

    body = str(element).rstrip()
    if str(element) == body:
        return

    if not body:
        node.insert_after(NavigableString(str(element)))
        element.decompose()
        return

    tail = str(element).split(body)[-1]
    after = node.next_sibling
    if isinstance(after, NavigableString):
        string = tail + str(after)
        after.replace_with(NavigableString(string))
    else:
        node.insert_after(NavigableString(tail))

    element.replace_with(NavigableString(body))


def _fix_newlines(soup: BeautifulSoup) -> None:
    # Remove linebreaks inside text nodes (as browser does)
    for node in soup(string=lambda s: isinstance(s, NavigableString) and "\n" in s):
        parents = {parent.name for parent in node.parents}
        if "code" in parents or "pre" in parents:
            continue

        string = str(node).replace("\n", " ")
        string = replace_rare_spaces(string)
        node.replace_with(NavigableString(string))


def _fix_inline(soup: BeautifulSoup) -> None:
    # Split inline elements
    for node in soup(inline_tags):
        before = node.previous_sibling
        if isinstance(before, NavigableString) and str(before) == str(before).rstrip():
            before.replace_with(NavigableString(f"{before}\u00a0"))
        if isinstance(before, Tag) and before.name in inline_tags:
            node.insert_before(NavigableString("\u00a0"))

        after = node.next_sibling
        if isinstance(after, NavigableString) and str(after) == str(after).lstrip():
            after.replace_with(NavigableString(f"\u00a0{after}"))
        if isinstance(after, Tag) and after.name in inline_tags:
            node.insert_after(NavigableString("\u00a0"))


def _fix_block(soup: BeautifulSoup) -> None:
    # Remove spaces at block element borders
    for node in soup(block_tags):
        if node.name in {"code", "pre"}:
            continue

        _fix_block_left(node)
        _fix_block_right(node)

        # Split block element
        if node.name != "br" and node.name not in child_tags:
            if node.previous_sibling:
                node.insert_before(soup.new_tag("br"))
            if node.next_sibling:
                node.insert_after(soup.new_tag("br"))


def _fix_block_left(node: Tag) -> None:
    # Around block element
    if isinstance(node.previous_sibling, NavigableString):
        string = str(node.previous_sibling).rstrip()
        if string:
            node.previous_sibling.replace_with(NavigableString(string))
        else:
            node.previous_sibling.decompose()

    # Inside block element
    if node.contents and isinstance(node.contents[0], NavigableString):
        string = str(node.contents[0]).lstrip()
        if string:
            node.contents[0].replace_with(NavigableString(string))
        else:
            node.contents[0].decompose()


def _fix_block_right(node: Tag) -> None:
    # Around block element
    if isinstance(node.next_sibling, NavigableString):
        string = str(node.next_sibling).lstrip()
        if string:
            node.next_sibling.replace_with(NavigableString(string))
        else:
            node.next_sibling.decompose()

    # Inside block element
    if node.contents and isinstance(node.contents[-1], NavigableString):
        string = str(node.contents[-1]).rstrip()
        if string:
            node.contents[-1].replace_with(NavigableString(string))
        else:
            node.contents[-1].decompose()


def _merge_siblings(element: PageElement) -> None:
    before = element.previous_sibling
    if isinstance(before, Comment):
        return
    if not isinstance(before, NavigableString):
        return

    after = element.next_sibling
    if isinstance(after, Comment):
        return
    if not isinstance(after, NavigableString):
        return

    string = str(before) + str(after)
    before.replace_with(NavigableString(string))
    after.decompose()
