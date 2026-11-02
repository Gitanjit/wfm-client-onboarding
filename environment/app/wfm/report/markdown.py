"""Plain table and number formatting for the reports, the client list and the notification digests.

Two renderings of the same rows: `table()` writes a GitHub-style markdown table (reports under
out/<client>/reports/, clients/README.md), `text_table()` an aligned plain-text table without pipes
(digests and agent notices, which are read as text).
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence

DASH = "-"


def num(x, digits: int = 1) -> str:
    """Fixed-point with thousands separators; None and NaN print as '-'."""
    if x is None or x != x:
        return DASH
    return f"{x:,.{digits}f}"


def ratio(x, digits: int = 3) -> str:
    """Attainment-style fraction, e.g. 0.937."""
    if x is None or x != x:
        return DASH
    return f"{x:.{digits}f}"


def pct(x, digits: int = 1) -> str:
    if x is None or x != x:
        return DASH
    return f"{100 * x:.{digits}f} %"


def change(x, digits: int = 1) -> str:
    """Signed relative change, e.g. '+3.2 %' or '-21.9 %'."""
    if x is None or x != x:
        return DASH
    return f"{100 * x:+.{digits}f} %"


def yes_no(flag) -> str:
    if flag is None:
        return DASH
    return "yes" if flag else "no"


def _cells(rows: Iterable[Sequence]) -> list[list[str]]:
    return [[DASH if c is None else str(c) for c in r] for r in rows]


def _is_numeric(s: str) -> bool:
    t = s.replace(",", "").replace("%", "").replace("+", "").replace(" ", "")
    if t.startswith("-") and t != DASH:
        t = t[1:]
    return t.replace(".", "", 1).isdigit()


def _alignments(headers: Sequence[str], body: list[list[str]], align: str | None) -> list[str]:
    """'l' or 'r' per column. Explicit `align` wins; otherwise a column whose cells are all numbers
    (or '-') is right-aligned."""
    if align is not None:
        if len(align) != len(headers):
            raise ValueError(f"align has {len(align)} entries for {len(headers)} columns")
        return list(align)
    out = []
    for i in range(len(headers)):
        col = [r[i] for r in body if r[i] != DASH]
        out.append("r" if col and all(_is_numeric(c) for c in col) else "l")
    return out


def _widths(headers: Sequence[str], body: list[list[str]]) -> list[int]:
    return [max([len(h)] + [len(r[i]) for r in body]) for i, h in enumerate(headers)]


def _pad(s: str, width: int, a: str) -> str:
    return s.rjust(width) if a == "r" else s.ljust(width)


def table(headers: Sequence[str], rows: Iterable[Sequence], align: str | None = None) -> str:
    """Markdown table with padded columns; numeric columns right-aligned."""
    body = _cells(rows)
    for r in body:
        if len(r) != len(headers):
            raise ValueError(f"row has {len(r)} cells for {len(headers)} columns: {r}")
    al = _alignments(headers, body, align)
    w = _widths(headers, body)
    lines = ["| " + " | ".join(_pad(h, w[i], al[i]) for i, h in enumerate(headers)) + " |",
             "|" + "|".join(("-" * (w[i] + 1) + ":") if al[i] == "r" else ("-" * (w[i] + 2))
                            for i in range(len(headers))) + "|"]
    for r in body:
        lines.append("| " + " | ".join(_pad(c, w[i], al[i]) for i, c in enumerate(r)) + " |")
    return "\n".join(lines)


def text_table(headers: Sequence[str], rows: Iterable[Sequence], align: str | None = None, indent: int = 2) -> str:
    """Aligned plain-text table: header, a rule, one line per row."""
    body = _cells(rows)
    al = _alignments(headers, body, align)
    w = _widths(headers, body)
    pad = " " * indent
    lines = [pad + "  ".join(_pad(h, w[i], al[i]) for i, h in enumerate(headers)).rstrip(),
             pad + "  ".join("-" * w[i] for i in range(len(headers)))]
    for r in body:
        lines.append(pad + "  ".join(_pad(c, w[i], al[i]) for i, c in enumerate(r)).rstrip())
    return "\n".join(lines)


def heading(title: str, level: int = 2) -> str:
    return f"{'#' * level} {title}"


def bullets(items: Iterable[str]) -> str:
    return "\n".join(f"- {i}" for i in items)


def document(*blocks: str) -> str:
    """Join non-empty blocks with blank lines; one trailing newline."""
    return "\n\n".join(b.rstrip("\n") for b in blocks if b) + "\n"
