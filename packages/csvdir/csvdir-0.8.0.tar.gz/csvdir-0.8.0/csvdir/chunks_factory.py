from __future__ import annotations
from .chunks_dir import CsvChunksDir

def read_dir_chunks(
    path: str | None,
    *,
    extension: str = "csv",
    delimiter: str = ",",
    chunksize: int = 1000,
    encoding: str = "utf-8",
    newline: str = "",
    quotechar: str = '"',
    escapechar: str | None = None,
    strict_headers: bool = False,
    expected_headers: list[str] | None = None,
    on_mismatch: str = "error",
    recurse: bool = False,
    case_insensitive: bool = True,
    include_hidden: bool = False,
) -> CsvChunksDir:
    """
    Factory for the chunked directory reader.
    """
    return CsvChunksDir(
        chunksize=chunksize,
        path=path,
        extension=extension,
        delimiter=delimiter,
        encoding=encoding,
        newline=newline,
        quotechar=quotechar,
        escapechar=escapechar,
        strict_headers=strict_headers,
        expected_headers=expected_headers,
        on_mismatch=on_mismatch,
        recurse=recurse,
        case_insensitive=case_insensitive,
        include_hidden=include_hidden,
    )