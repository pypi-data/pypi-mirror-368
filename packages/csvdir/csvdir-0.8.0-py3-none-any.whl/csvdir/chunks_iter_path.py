from __future__ import annotations

from dataclasses import dataclass, field
import csv
from typing import Dict, List, Tuple, Optional, Generator

from .pathing import get_csv_paths
from .utils import (
    pick_encoding,
    sniff_quotechar,
    read_header as _read_header,
    check_headers as _check_headers,
    strip_bom_from_headers,
)


@dataclass(slots=True)
class IterPathCsvChunksDir:
    chunksize: int
    path: Optional[str] = None
    extension: str = "csv"
    delimiter: str = ","
    encoding: str = "utf-8"
    newline: str = ""
    quotechar: str = '"'
    escapechar: Optional[str] = None
    strict_headers: bool = False
    expected_headers: Optional[List[str]] = None
    on_mismatch: str = "error"
    recurse: bool = False
    case_insensitive: bool = True
    include_hidden: bool = False

    _it: Optional[Generator[Tuple[str, List[Dict[str, str]]], None, None]] = field(
        init=False, default=None, repr=False
    )

    def __iter__(self) -> "IterPathCsvChunksDir":
        self._it = self._gen()
        return self

    def __next__(self) -> Tuple[str, List[Dict[str, str]]]:
        if self._it is None:
            self._it = self._gen()
        return next(self._it)

    def _gen(self) -> Generator[Tuple[str, List[Dict[str, str]]], None, None]:
        canonical = list(self.expected_headers) if self.expected_headers else None
        for p in get_csv_paths(
            self.path or ".",
            self.extension,
            recurse=self.recurse,
            case_insensitive=self.case_insensitive,
            include_hidden=self.include_hidden,
        ):
            file_headers = _read_header(
                p,
                encoding=self.encoding,
                newline=self.newline,
                delimiter=self.delimiter,
                quotechar=self.quotechar,
                escapechar=self.escapechar,
            )
            if self.strict_headers and canonical is None:
                canonical = file_headers
            expected = canonical or self.expected_headers
            if expected is not None:
                match, missing, extra = _check_headers(file_headers, expected)
                if not match:
                    if self.on_mismatch == "skip":
                        continue
                    detail: List[str] = []
                    if missing:
                        detail.append(f"missing columns: {missing}")
                    if extra:
                        detail.append(f"extra columns: {extra}")
                    raise ValueError(f"Header mismatch in '{p}': " + "; ".join(detail))

            enc = pick_encoding(p, self.encoding, self.newline)
            with open(p, newline=self.newline, encoding=enc) as f:
                qc = sniff_quotechar(
                    p,
                    delimiter=self.delimiter,
                    encoding=enc,
                    newline=self.newline,
                    fallback=self.quotechar or '"',
                )
                reader = csv.DictReader(
                    f,
                    delimiter=self.delimiter,
                    quotechar=qc,
                    escapechar=self.escapechar,
                )
                if reader.fieldnames:
                    reader.fieldnames = strip_bom_from_headers(reader.fieldnames)

                chunk: List[Dict[str, str]] = []
                for row in reader:
                    chunk.append({k: ("" if v is None else str(v)) for k, v in row.items()})
                    if len(chunk) >= self.chunksize:
                        yield (p, chunk)
                        chunk = []
                if chunk:
                    yield (p, chunk)

    # -------- column selection helpers (chunked) --------

    def iter_column_chunks(self, column_name: str, chunk_size: Optional[int] = None):
        cs = self.chunksize if chunk_size is None else int(chunk_size)
        canonical = list(self.expected_headers) if self.expected_headers else None

        for p in get_csv_paths(
            self.path or ".", self.extension,
            recurse=self.recurse, case_insensitive=self.case_insensitive,
            include_hidden=self.include_hidden
        ):
            file_headers = _read_header(
                p, encoding=self.encoding, newline=self.newline,
                delimiter=self.delimiter, quotechar=self.quotechar, escapechar=self.escapechar,
            )
            if self.strict_headers and canonical is None:
                canonical = file_headers
            expected = canonical or self.expected_headers
            if expected is not None:
                match, missing, extra = _check_headers(file_headers, expected)
                if not match:
                    if self.on_mismatch == "skip":
                        continue
                    detail: List[str] = []
                    if missing: detail.append(f"missing columns: {missing}")
                    if extra: detail.append(f"extra columns: {extra}")
                    raise ValueError(f"Header mismatch in '{p}': " + "; ".join(detail))

            if column_name not in file_headers:
                if self.on_mismatch == "skip":
                    continue
                raise ValueError(f"Column '{column_name}' not found in '{p}'")

            enc = pick_encoding(p, self.encoding, self.newline)
            with open(p, "r", encoding=enc, newline=self.newline) as f:
                qc = sniff_quotechar(
                    p, delimiter=self.delimiter, encoding=enc, newline=self.newline,
                    fallback=self.quotechar or '"',
                )
                reader = csv.DictReader(f, delimiter=self.delimiter, quotechar=qc, escapechar=self.escapechar)
                if reader.fieldnames:
                    reader.fieldnames = strip_bom_from_headers(reader.fieldnames)

                out: List[str] = []
                for row in reader:
                    v = row.get(column_name)
                    out.append("" if v is None else str(v))
                    if len(out) >= cs:
                        yield (p, out)
                        out = []
                if out:
                    yield (p, out)

    def select_columns_chunks(self, columns: List[str], chunk_size: Optional[int] = None):
        cs = self.chunksize if chunk_size is None else int(chunk_size)
        canonical = list(self.expected_headers) if self.expected_headers else None

        for p in get_csv_paths(
            self.path or ".", self.extension,
            recurse=self.recurse, case_insensitive=self.case_insensitive,
            include_hidden=self.include_hidden
        ):
            file_headers = _read_header(
                p, encoding=self.encoding, newline=self.newline,
                delimiter=self.delimiter, quotechar=self.quotechar, escapechar=self.escapechar,
            )
            if self.strict_headers and canonical is None:
                canonical = file_headers
            expected = canonical or self.expected_headers
            if expected is not None:
                match, missing, extra = _check_headers(file_headers, expected)
                if not match:
                    if self.on_mismatch == "skip":
                        continue
                    detail: List[str] = []
                    if missing: detail.append(f"missing columns: {missing}")
                    if extra: detail.append(f"extra columns: {extra}")
                    raise ValueError(f"Header mismatch in '{p}': " + "; ".join(detail))

            missing_req = [c for c in columns if c not in file_headers]
            if missing_req:
                if self.on_mismatch == "skip":
                    continue
                raise ValueError(f"Missing requested columns in '{p}': {missing_req}")

            enc = pick_encoding(p, self.encoding, self.newline)
            with open(p, "r", encoding=enc, newline=self.newline) as f:
                qc = sniff_quotechar(
                    p, delimiter=self.delimiter, encoding=enc, newline=self.newline,
                    fallback=self.quotechar or '"',
                )
                reader = csv.DictReader(f, delimiter=self.delimiter, quotechar=qc, escapechar=self.escapechar)
                if reader.fieldnames:
                    reader.fieldnames = strip_bom_from_headers(reader.fieldnames)

                out: List[Dict[str, str]] = []
                for row in reader:
                    item: Dict[str, str] = {}
                    for c in columns:
                        v = row.get(c)
                        item[c] = "" if v is None else str(v)
                    out.append(item)
                    if len(out) >= cs:
                        yield (p, out)
                        out = []
                if out:
                    yield (p, out)