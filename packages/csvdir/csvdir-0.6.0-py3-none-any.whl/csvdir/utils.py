from __future__ import annotations

import csv
from typing import List, Optional, Tuple


def strip_bom_from_headers(cols: List[str]) -> List[str]:
    """Remove a UTF-8 BOM marker from the start of header names."""
    return [c.lstrip("\ufeff") if isinstance(c, str) else c for c in cols]


def pick_encoding(path: str, preferred: str, newline: str) -> str:
    """Choose a working text encoding for this file.
    Try the preferred encoding first, then safe fallbacks.
    Reject decodes that contain NULs (common when mis-decoding UTF-16 as UTF-8).
    """
    candidates = [preferred, "utf-8", "utf-8-sig", "utf-16-le", "utf-16-be"]
    for enc in candidates:
        try:
            with open(path, "r", encoding=enc, newline=newline) as f:
                text = f.read(2048)
            if "\x00" in text:
                continue
            return enc
        except UnicodeError:
            continue
        except Exception:
            return preferred or "utf-8"
    return preferred or "utf-8"


def sniff_quotechar(
    path: str,
    *,
    delimiter: str,
    encoding: str,
    newline: str,
    fallback: str,
) -> str:
    """Detect quotechar from a sample; prefer a char actually wrapping fields
    containing the delimiter, then try csv.Sniffer, then smart fallbacks.
    """
    import re

    try:
        with open(path, "r", encoding=encoding, newline=newline) as f:
            sample = f.read(4096)
    except Exception:
        return fallback or '"'

    def looks_like_quoting(qc: str) -> bool:
        if not qc:
            return False
        pat = rf'{re.escape(qc)}[^{re.escape(qc)}\n]*{re.escape(delimiter)}[^{re.escape(qc)}\n]*{re.escape(qc)}'
        return re.search(pat, sample) is not None

    for cand in ('"', "'"):
        if looks_like_quoting(cand):
            return cand

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=delimiter)
        qc = getattr(dialect, "quotechar", None)
        if qc:
            return qc
    except Exception:
        pass

    def has_paired(qc: str) -> bool:
        if not qc:
            return False
        return re.search(rf'{re.escape(qc)}[^{re.escape(qc)}\n]+{re.escape(qc)}', sample) is not None

    if fallback and has_paired(fallback):
        return fallback
    for cand in ('"', "'"):
        if cand != fallback and has_paired(cand):
            return cand

    return fallback or '"'


def read_header(
    path: str,
    *,
    encoding: str = "utf-8",
    newline: str = "",
    delimiter: str = ",",
    quotechar: str = '"',
    escapechar: Optional[str] = None,
) -> List[str]:
    """Return the header row for a CSV file, with BOM stripped and quoting auto-detected."""
    chosen_enc = pick_encoding(path, encoding, newline)
    qc = sniff_quotechar(
        path,
        delimiter=delimiter,
        encoding=chosen_enc,
        newline=newline,
        fallback=quotechar or '"',
    )
    with open(path, "r", encoding=chosen_enc, newline=newline) as f:
        reader = csv.reader(f, delimiter=delimiter, quotechar=qc, escapechar=escapechar)
        header = next(reader, [])
        return strip_bom_from_headers(header)


def check_headers(file_headers: List[str], expected: List[str]) -> Tuple[bool, List[str], List[str]]:
    """Compare two header lists; return (match, missing_in_file, extra_in_file)."""
    set_file = set(file_headers)
    set_exp = set(expected)
    missing = sorted(list(set_exp - set_file))
    extra = sorted(list(set_file - set_exp))
    return (not missing and not extra, missing, extra)
