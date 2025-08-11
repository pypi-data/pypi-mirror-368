from __future__ import annotations

from dataclasses import dataclass
import csv
from typing import Dict, Iterator, List, Tuple, Optional

from .pathing import get_csv_paths, get_name
from .utils import (
    pick_encoding,
    sniff_quotechar,
    read_header as _read_header,
    check_headers as _check_headers,
)

__all__ = ["IterEnumCsvChunksDir", "IterPathCsvChunksDir"]


@dataclass
class IterEnumCsvChunksDir:
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
    # directory options
    recurse: bool = False
    case_insensitive: bool = True
    include_hidden: bool = False

    def __iter__(self) -> Iterator[Tuple[str, List[Dict[str, str]]]]:
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
                    detail = []
                    if missing:
                        detail.append(f"missing columns: {missing}")
                    if extra:
                        detail.append(f"extra columns: {extra}")
                    raise ValueError(f"Header mismatch in '{p}': " + "; ".join(detail))
            name = get_name(p)

            chosen_enc = pick_encoding(p, self.encoding, self.newline)
            with open(p, newline=self.newline, encoding=chosen_enc) as f:
                qc = sniff_quotechar(
                    p,
                    delimiter=self.delimiter,
                    encoding=chosen_enc,
                    newline=self.newline,
                    fallback=self.quotechar or '"',
                )
                reader = csv.DictReader(
                    f,
                    delimiter=self.delimiter,
                    quotechar=qc,
                    escapechar=self.escapechar,
                )
                chunk: List[Dict[str, str]] = []
                for row in reader:
                    chunk.append({k: ("" if v is None else str(v)) for k, v in row.items()})
                    if len(chunk) >= self.chunksize:
                        yield (name, chunk)
                        chunk = []
                if chunk:
                    yield (name, chunk)


@dataclass
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
    # directory options
    recurse: bool = False
    case_insensitive: bool = True
    include_hidden: bool = False

    def __iter__(self) -> Iterator[Tuple[str, List[Dict[str, str]]]]:
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
                    detail = []
                    if missing:
                        detail.append(f"missing columns: {missing}")
                    if extra:
                        detail.append(f"extra columns: {extra}")
                    raise ValueError(f"Header mismatch in '{p}': " + "; ".join(detail))

            chosen_enc = pick_encoding(p, self.encoding, self.newline)
            with open(p, newline=self.newline, encoding=chosen_enc) as f:
                qc = sniff_quotechar(
                    p,
                    delimiter=self.delimiter,
                    encoding=chosen_enc,
                    newline=self.newline,
                    fallback=self.quotechar or '"',
                )
                reader = csv.DictReader(
                    f,
                    delimiter=self.delimiter,
                    quotechar=qc,
                    escapechar=self.escapechar,
                )
                chunk: List[Dict[str, str]] = []
                for row in reader:
                    chunk.append({k: ("" if v is None else str(v)) for k, v in row.items()})
                    if len(chunk) >= self.chunksize:
                        yield (p, chunk)
                        chunk = []
                if chunk:
                    yield (p, chunk)
