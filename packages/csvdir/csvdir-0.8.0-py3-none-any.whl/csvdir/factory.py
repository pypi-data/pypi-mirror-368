from __future__ import annotations

from typing import Optional, List
from .dir_reader import CsvDir
from .chunks_dir import CsvChunksDir


def read_dir(
    path: Optional[str] = None,
    *,
    extension: str = "csv",
    delimiter: str = ",",
    chunksize: Optional[int] = None,
    encoding: str = "utf-8",
    newline: str = "",
    quotechar: str = '"',
    escapechar: Optional[str] = None,
    strict_headers: bool = False,
    expected_headers: Optional[List[str]] = None,
    on_mismatch: str = "error",
    recurse: bool = False,
    case_insensitive: bool = True,
    include_hidden: bool = False,
):
    if chunksize:
        return CsvChunksDir(
            chunksize,
            path,
            extension,
            delimiter,
            encoding,
            newline,
            quotechar,
            escapechar,
            strict_headers,
            expected_headers,
            on_mismatch,
            recurse,
            case_insensitive,
            include_hidden,
        )
    return CsvDir(
        path,
        extension,
        delimiter,
        encoding,
        newline,
        quotechar,
        escapechar,
        strict_headers,
        expected_headers,
        on_mismatch,
        recurse,
        case_insensitive,
        include_hidden,
    )
