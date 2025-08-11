from __future__ import annotations

from typing import Optional, List
from .chunks_dir import CsvChunksDir

def read_dir_chunks(
    path: Optional[str],
    *,
    extension: str = "csv",
    delimiter: str = ",",
    chunksize: int = 1000,
    encoding: str = "utf-8",
    newline: str = "",
    quotechar: str = '"',
    escapechar: Optional[str] = None,
    strict_headers: bool = False,
    expected_headers: Optional[List[str]] = None,
    on_mismatch: str = "error",
    # directory options
    recurse: bool = False,
    case_insensitive: bool = True,
    include_hidden: bool = False,
) -> CsvChunksDir:
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
