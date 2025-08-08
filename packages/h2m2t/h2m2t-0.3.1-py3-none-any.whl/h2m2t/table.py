import copy
from itertools import groupby, pairwise

from bs4 import BeautifulSoup, Tag

# According to https://html.spec.whatwg.org/multipage/tables.html#attributes-common-to-td-and-th-elements
# and https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/td#attributes
max_rowspan: int = 65534
max_colspan: int = 1000


def tables_to_dense(soup: BeautifulSoup, *, deduplicate: bool, unwrap: bool) -> None:
    for table in reversed(soup("table")):
        _normalize_table_parts(table, deduplicate=deduplicate)
        if unwrap:
            _unwrap_empty_table(table)


def _normalize_table_parts(table: Tag, *, deduplicate: bool) -> None:
    cells: list[list[Tag]] = []

    # Fix cell spans for each part separately
    for thead in table("thead", recursive=False):
        cells.extend(_fix_cell_spans(thead("tr", recursive=False)))

    body: list[Tag] = []
    for tbody_or_tr in table(["tbody", "tr"], recursive=False):
        if tbody_or_tr.name == "tbody":
            cells.extend(_fix_cell_spans(body))
            body = []
            cells.extend(_fix_cell_spans(tbody_or_tr("tr", recursive=False)))
        else:
            body.append(tbody_or_tr)
    cells.extend(_fix_cell_spans(body))

    for tfoot in table("tfoot", recursive=False):
        cells.extend(_fix_cell_spans(tfoot("tr", recursive=False)))

    # Build virtual grid with references to cells
    grid = _build_virtual_grid(cells)

    if deduplicate:
        # Drop repeating rows
        grid = _cleanup_virtual_grid(grid, transpose=False)
        # ... and columns
        grid = _cleanup_virtual_grid(grid, transpose=True)

    # Group rows by original parent group name
    parts = {part: list(rows) for part, rows in groupby(grid, lambda r: _estimate_rows_parent(r, cells))}

    # Move caption before table
    for caption in table("caption", recursive=False):
        caption.name = "div"
        table.insert_before(caption.extract())

    # Build new table content
    tparts = []
    for part in ["thead", "tbody", "tfoot"]:
        tbody = Tag(name=part)
        for row in parts.get(part, []):
            tr = Tag(name="tr")
            for rc in row:
                td = copy.deepcopy(cells[rc[0]][rc[1]]) if rc else Tag(name="td")
                tr.append(td)
            if tr.contents:
                tbody.append(tr)
        if tbody.contents:
            tparts.append(tbody)

    # Replace table content
    table.clear()
    table.extend(tparts)


def _fix_cell_spans(rows: list[Tag]) -> list[list[Tag]]:
    grid: list[list[Tag]] = [r(["th", "td"], recursive=False) for r in rows]

    for r, row in enumerate(grid):
        for cell in row:
            rowspan = int(cell.get("rowspan", "1") or "1")
            rowspan = 1 if rowspan < 0 else rowspan
            rowspan = max_rowspan if rowspan == 0 else rowspan
            rowspan = min(rowspan, len(rows) - r)
            cell["rowspan"] = str(rowspan)

            colspan = int(cell.get("colspan", "1") or "1")
            colspan = 1 if colspan < 1 or colspan > max_colspan else colspan
            colspan = min(max(colspan, 1), max_colspan)
            cell["colspan"] = str(colspan)

    return grid


def _build_virtual_grid(cells: list[list[Tag]]) -> list[list[tuple[int, int] | None]]:
    grid: list[list[tuple[int, int] | None]] = [[] for _ in range(len(cells))]

    for r, row in enumerate(cells):
        for c, cell in enumerate(row):
            rowspan = int(cell.get("rowspan"))
            colspan = int(cell.get("colspan"))
            del cell["rowspan"], cell["colspan"]

            for ri in range(r, len(cells)):
                grid[ri].extend([None] * colspan)

            c_empty = grid[r].index(None)

            for rs in range(r, r + rowspan):
                for cs in range(c_empty, c_empty + colspan):
                    grid[rs][cs] = (r, c)

    maxlen = max([max([c for c, cell in enumerate(row) if cell], default=-1) for row in grid], default=-1) + 1
    return [row[:maxlen] + [None] * (maxlen - len(row)) for row in grid]


def _cleanup_virtual_grid(
    grid: list[list[tuple[int, int] | None]],
    *,
    transpose: bool,
) -> list[list[tuple[int, int] | None]]:
    if transpose:
        grid = [list(row) for row in zip(*grid, strict=True)]

    equals = [i for i, (row0, row1) in enumerate(pairwise(grid)) if row0 == row1]
    for i in reversed(equals):
        del grid[i + 1]

    if transpose:
        grid = [list(row) for row in zip(*grid, strict=True)]

    return grid


def _unwrap_empty_table(table: Tag) -> None:
    def _drop_table() -> None:
        caption = table.find("caption", recursive=False)
        if caption:
            caption = copy.deepcopy(caption)
            caption.name = "div"
            table.insert_before(caption)
        table.decompose()

    rows = table("tr", recursive=False)
    for body in table(["thead", "tbody", "tfoot"], recursive=False):
        rows.extend(body("tr", recursive=False))
    cells = [cell for row in rows for cell in row(["th", "td"], recursive=False)]
    cells = [cell for cell in cells if cell.text.strip()]

    if not cells:
        _drop_table()
    elif len(cells) == 1:
        cell = copy.deepcopy(cells[0])
        cell.name = "div"
        table.insert_after(cell)
        _drop_table()


def _estimate_rows_parent(row: list[tuple[int, int] | None], cells: list[list[Tag]]) -> str:
    for rc in row:
        if not rc:
            continue
        cell = cells[rc[0]][rc[1]]
        parent = cell.find_parent(["thead", "tbody", "tfoot", "table"])

        if not parent:
            continue

        if parent.name in {"thead", "tbody", "tfoot"}:
            return parent.name

    return "tbody"
