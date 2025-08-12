from __future__ import annotations

from dataclasses import dataclass
import csv
from typing import Dict, Iterator, List, Optional

from .pathing import get_csv_paths
from .utils import (
    pick_encoding,
    sniff_quotechar,
    read_header as _read_header,
    check_headers as _check_headers,
    strip_bom_from_headers,
)
from .iter_path import IterPathCsvDir
from .iter_enum import IterEnumCsvDir


@dataclass(slots=True)
class CsvDir:
    path: Optional[str] = None
    extension: str = "csv"
    delimiter: str = ","
    encoding: str = "utf-8"
    newline: str = ""
    quotechar: str = '"'
    escapechar: Optional[str] = None
    strict_headers: bool = False
    expected_headers: Optional[List[str]] = None
    on_mismatch: str = "error"  # 'error' or 'skip'
    # directory walking options
    recurse: bool = False
    case_insensitive: bool = True
    include_hidden: bool = False

    def __iter__(self) -> Iterator[Dict[str, str]]:
        for p in self.paths:
            for row in self._iter_file(p):
                yield row

    # ---------- properties ----------

    @property
    def paths(self) -> List[str]:
        base = self.path or "."
        return list(
            get_csv_paths(
                base,
                self.extension,
                recurse=self.recurse,
                case_insensitive=self.case_insensitive,
                include_hidden=self.include_hidden,
            )
        )

    @property
    def names(self) -> List[str]:
        # derive stems from discovered paths
        from .pathing import get_name
        return [get_name(p) for p in self.paths]

    # ---------- internal ----------

    def _iter_file(self, p: str) -> Iterator[Dict[str, str]]:
        # header check
        file_headers = _read_header(
            p,
            encoding=self.encoding,
            newline=self.newline,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
        )

        expected = self.expected_headers
        if self.strict_headers and expected is None:
            self.expected_headers = file_headers
            expected = file_headers
        if expected is not None:
            match, missing, extra = _check_headers(file_headers, expected)
            if not match:
                if self.on_mismatch == "skip":
                    return
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

            for row in reader:
                yield {k: ("" if v is None else str(v)) for k, v in row.items()}

    # ---------- helper iterators ----------

    def with_paths(self) -> IterPathCsvDir:
        return IterPathCsvDir(
            self.path,
            extension=self.extension,
            delimiter=self.delimiter,
            encoding=self.encoding,
            newline=self.newline,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
            strict_headers=self.strict_headers,
            expected_headers=list(self.expected_headers) if self.expected_headers else None,
            on_mismatch=self.on_mismatch,
            recurse=self.recurse,
            case_insensitive=self.case_insensitive,
            include_hidden=self.include_hidden,
        )

    def enumerate(self) -> IterEnumCsvDir:
        return IterEnumCsvDir(
            self.path,
            extension=self.extension,
            delimiter=self.delimiter,
            encoding=self.encoding,
            newline=self.newline,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
            strict_headers=self.strict_headers,
            expected_headers=list(self.expected_headers) if self.expected_headers else None,
            on_mismatch=self.on_mismatch,
            recurse=self.recurse,
            case_insensitive=self.case_insensitive,
            include_hidden=self.include_hidden,
        )

    def with_names(self) -> IterEnumCsvDir:
        """Alias for enumerate(); tests expect names without extension here."""
        return self.enumerate()