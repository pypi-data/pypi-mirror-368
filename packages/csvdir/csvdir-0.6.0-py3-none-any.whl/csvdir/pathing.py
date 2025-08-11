import os
from typing import List


def get_name(path: str) -> str:
    """Return the filename without its extension."""
    return os.path.splitext(os.path.basename(path))[0]


def _has_extension(path: str, extension: str, *, case_insensitive: bool = True) -> bool:
    """Check if the file has the given extension."""
    _, ext = os.path.splitext(path)
    if not ext:
        return False
    ext = ext[1:]  # drop the leading dot
    return ext.lower() == extension.lower() if case_insensitive else ext == extension


def get_csv_paths(
    path: str,
    extension: str,
    *,
    recurse: bool = False,
    case_insensitive: bool = True,
    include_hidden: bool = False,
) -> List[str]:
    """
    Return sorted file paths under *path* with the given extension.

    Args:
        path: Directory to search.
        extension: File extension (without the dot).
        recurse: If True, searches subdirectories recursively.
        case_insensitive: If True, extension matching ignores case.
        include_hidden: If True, includes files and directories starting with '.'.
    """
    path = os.fspath(path or '.')
    results: List[str] = []
    if recurse:
        for dirpath, dirnames, filenames in os.walk(path):
            if not include_hidden:
                # Avoid descending into hidden directories
                dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            for fn in filenames:
                if not include_hidden and fn.startswith('.'):
                    continue
                fp = os.path.join(dirpath, fn)
                if _has_extension(fp, extension, case_insensitive=case_insensitive):
                    results.append(fp)
    else:
        try:
            for fn in os.listdir(path):
                if not include_hidden and fn.startswith('.'):
                    continue
                fp = os.path.join(path, fn)
                if os.path.isfile(fp) and _has_extension(fp, extension, case_insensitive=case_insensitive):
                    results.append(fp)
        except FileNotFoundError:
            # Mirror prior behavior: return empty list if path missing
            return []
    results.sort()
    return results
