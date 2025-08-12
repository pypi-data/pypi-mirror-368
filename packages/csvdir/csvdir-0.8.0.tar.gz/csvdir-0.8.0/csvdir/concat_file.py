from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple

from .pathing import get_csv_paths
from .utils import pick_encoding, read_header as _read_header


def _strip_bom_from_line(s: str) -> str:
    if s and s[0] == "\ufeff":
        return s[1:]
    return s


def _headers_match_seq(file_headers: List[str], canonical: List[str]) -> bool:
    return list(file_headers) == list(canonical)


@dataclass
class CsvDirFile:
    """
    File-like object that concatenates CSV files in a directory into one logical CSV stream.
    - Emits the header once (from the first matching file).
    - Skips headers on later files only if they match the canonical header (sequence-sensitive).

    pandas compatibility:
      - read(size=-1), readline(), readlines(), iteration
      - seek(0) to restart (other seeks raise)
      - tell(), readable(), seekable(), close(), context manager

    Note: We keep a small string buffer to satisfy size-bounded reads. Data is produced lazily from
    the underlying files; we do not load everything into memory.
    """

    # Directory scanning
    path: Optional[str] = None
    extension: str = "csv"
    recurse: bool = False
    case_insensitive: bool = True
    include_hidden: bool = False

    # Header parsing / canonical selection
    delimiter: str = ","
    quotechar: str = '"'
    escapechar: Optional[str] = None

    # IO options
    encoding: str = "utf-8"
    newline: str = ""

    # Header policy
    strict_headers: bool = False  # kept for API symmetry
    expected_headers: Optional[List[str]] = None
    on_mismatch: str = "error"  # "error" or "skip"

    # Internal streaming state
    _gen: Optional[Iterator[str]] = None     # line generator for the stitched stream
    _buf: str = ""                           # unread tail from last read
    _pos: int = 0                            # logical position in the concatenated stream
    _closed: bool = False

    # -------------------- std io API --------------------

    def __enter__(self) -> "CsvDirFile":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        self._gen = None
        self._buf = ""
        self._closed = True

    @property
    def closed(self) -> bool:
        return self._closed

    def readable(self) -> bool:
        return not self._closed

    def seekable(self) -> bool:
        # We support seek(0) (restart). Other seeks raise UnsupportedOperation.
        return True

    def tell(self) -> int:
        return self._pos

    def seek(self, offset: int, whence: int = 0) -> int:
        if self._closed:
            raise ValueError("I/O operation on closed CsvDirFile")
        if whence == 0 and offset == 0:
            # restart stream
            self._reset_stream()
            return self._pos
        if whence == 1 and offset == 0:
            # no-op
            return self._pos
        raise io.UnsupportedOperation("CsvDirFile only supports seek(0, 0) and seek(0, 1)")

    # Iteration yields lines
    def __iter__(self) -> Iterator[str]:
        while True:
            line = self.readline()
            if not line:
                break
            yield line

    # Size-bounded read
    def read(self, size: int = -1) -> str:
        self._ensure_gen()
        if size is None or size < 0:
            # drain everything
            chunks = [self._buf]
            self._pos += len(self._buf)
            self._buf = ""
            for line in self._gen:  # type: ignore[arg-type]
                chunks.append(line)
                self._pos += len(line)
            return "".join(chunks)

        # ensure at least size bytes in buffer (or EOF)
        out = io.StringIO()
        while len(self._buf) < size:
            nxt = self._next_line_or_eof()
            if nxt is None:
                break
            self._buf += nxt
        # slice out requested bytes
        take = self._buf[:size]
        self._buf = self._buf[size:]
        self._pos += len(take)
        out.write(take)
        return out.getvalue()

    def readline(self) -> str:
        self._ensure_gen()
        # fill buffer until newline or EOF
        idx = self._buf.find("\n")
        while idx < 0:
            nxt = self._next_line_or_eof()
            if nxt is None:
                break
            self._buf += nxt
            idx = self._buf.find("\n")

        if idx >= 0:
            # include newline
            line = self._buf[: idx + 1]
            self._buf = self._buf[idx + 1 :]
        else:
            # last line without newline (EOF)
            line = self._buf
            self._buf = ""

        self._pos += len(line)
        return line

    def readlines(self) -> List[str]:
        lines: List[str] = []
        while True:
            ln = self.readline()
            if not ln:
                break
            lines.append(ln)
        return lines

    # -------------------- internals --------------------

    def _reset_stream(self) -> None:
        self._gen = None
        self._buf = ""
        self._pos = 0
        self._closed = False
        self._ensure_gen()

    def _ensure_gen(self) -> None:
        if self._closed:
            raise ValueError("I/O operation on closed CsvDirFile")
        if self._gen is None:
            self._gen = self._line_generator()

    def _next_line_or_eof(self) -> Optional[str]:
        assert self._gen is not None
        try:
            return next(self._gen)
        except StopIteration:
            return None

    def _line_generator(self) -> Iterator[str]:
        """
        Build a continuous CSV stream with a single header:
          1) List files (deterministic).
          2) Pre-scan headers using utils.read_header.
          3) Choose canonical header (expected or lexicographically smallest).
          4) Emit the header+body from first matching file.
          5) For remaining files: if header matches -> skip header then emit body;
             else skip or raise based on on_mismatch.
        """
        base = self.path or "."
        paths = get_csv_paths(
            base,
            self.extension,
            recurse=self.recurse,
            case_insensitive=self.case_insensitive,
            include_hidden=self.include_hidden,
        )
        if not paths:
            return
            yield  # pragma: no cover

        # Pre-scan headers deterministically
        header_index: List[Tuple[str, List[str]]] = []
        for p in paths:
            hs = _read_header(
                p,
                encoding=self.encoding,
                newline=self.newline,
                delimiter=self.delimiter,
                quotechar=self.quotechar,
                escapechar=self.escapechar,
            )
            header_index.append((p, hs))

        # Canonical header
        if self.expected_headers:
            canonical = list(self.expected_headers)
        else:
            if not header_index:
                return
                yield  # pragma: no cover
            def _key(hs: List[str]) -> str:
                return self.delimiter.join(hs)
            canonical = min((hs for _, hs in header_index), key=_key)

        # First matching file (for header emission)
        first_path: Optional[str] = None
        for p, hs in header_index:
            if _headers_match_seq(hs, canonical):
                first_path = p
                break
        if first_path is None:
            if self.on_mismatch == "skip":
                return
                yield  # pragma: no cover
            bad_p, bad_h = header_index[0]
            raise ValueError(f"Header mismatch in '{bad_p}': expected {canonical} got {bad_h}")

        # Emit header + body of first matching file
        enc = pick_encoding(first_path, self.encoding, self.newline)
        with open(first_path, "r", encoding=enc, newline=self.newline) as f:
            header_line = f.readline()
            header_line = _strip_bom_from_line(header_line)
            if header_line and not header_line.endswith(("\n", "\r")):
                header_line += "\n"
            if header_line:
                yield header_line
            for line in f:
                yield line

        # Remaining files
        idx_first = paths.index(first_path)
        remaining = paths[:idx_first] + paths[idx_first + 1 :]
        hdr_map = dict(header_index)

        for p in remaining:
            hs = hdr_map[p]
            if _headers_match_seq(hs, canonical):
                enc = pick_encoding(p, self.encoding, self.newline)
                with open(p, "r", encoding=enc, newline=self.newline) as f:
                    _ = f.readline()  # skip header
                    for line in f:
                        yield line
            else:
                if self.on_mismatch == "skip":
                    continue
                raise ValueError(f"Header mismatch in '{p}': expected {canonical} got {hs}")


__all__ = ["CsvDirFile"]
