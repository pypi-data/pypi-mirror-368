from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any, override

from .drawable import Drawable, Marker
from .fill import Fill


class Grid(Drawable):
    columns: tuple[int | None, ...]
    rows: list[tuple["Drawable | Cell", ...]]

    def __init__(
        self,
        columns: tuple[int | None, ...],
        rows: Iterable[tuple[Drawable, ...]],
    ):
        self.columns = columns
        self.rows = []

        for row in rows:
            assert len(row) == len(self.columns)
            self.rows.append(row)

    @override
    def base_width(self) -> int:
        base_width = 0

        for col, weight in enumerate(self.columns):
            if weight is not None:
                continue

            col_width = 0
            for row in self.rows:
                col_width = max(col_width, row[col].base_width())

            base_width += col_width

        return base_width

    @override
    def _render(self, width: int, height: int | None) -> Iterator[str | Marker[Any]]:
        # First start by filling the widths of fixed columns and getting the
        # total weight
        col_widths: list[int] = []
        total_weight = 0

        for col, weight in enumerate(self.columns):
            col_width = 0

            if weight is None:
                for row in self.rows:
                    col_width = max(col_width, row[col].base_width())
            else:
                total_weight += weight

            col_widths.append(col_width)

        # Then divide the leftover space over the weighted columns
        total_space = width - sum(col_widths)
        cum_weight = 0
        cum_space = 0

        for col, weight in enumerate(self.columns):
            if weight is None:
                continue

            cum_weight += weight
            col_width = round(total_space * cum_weight / total_weight) - cum_space
            cum_space += col_width

            col_widths[col] = col_width

        # Now we can render the rows
        for row in self.rows:
            row_lines: list[list[str]] = []
            row_markers: list[list[Marker[Any]]] = []

            for col, cell in enumerate(row):
                y = 0
                col_width = col_widths[col]

                for cell_line in cell._render(col_width, height):
                    if isinstance(cell_line, Marker):
                        if y == 0:
                            yield cell_line
                        else:
                            row_markers[y - 1].append(cell_line)
                        continue

                    if y == len(row_lines):
                        row_lines.append([])
                        for x in range(col):
                            row_lines[y].append(cell_padding(row[x], col_widths[x]))
                        row_markers.append([])

                    row_lines[y].append(cell_line)
                    y += 1

                while y < len(row_lines):
                    row_lines[y].append(cell_padding(cell, col_width))
                    y += 1

            for row_line, markers in zip(row_lines, row_markers):
                yield "".join(row_line)
                yield from markers

            if height is not None:
                height -= len(row_lines)

    @dataclass
    class Cell(Drawable):
        drawable: Drawable
        padding: Drawable

        @override
        def base_width(self) -> int:
            return self.drawable.base_width()

        @override
        def _render(
            self, width: int, height: int | None
        ) -> Iterator[str | Marker[Any]]:
            return self.drawable._render(width, height)


def cell_padding(drawable: Drawable, width: int) -> str:
    if isinstance(drawable, Grid.Cell):
        padding = drawable.padding
    else:
        padding = Fill()
    return next(padding.render(width, 1))
