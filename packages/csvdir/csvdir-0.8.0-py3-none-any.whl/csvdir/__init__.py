__version__ = '0.8.0'

from .factory import read_dir
from .chunks_factory import read_dir_chunks
from .dir_reader import CsvDir
from .chunks_dir import CsvChunksDir
from .concat_file import CsvDirFile

__all__ = [
    "read_dir",
    "read_dir_chunks",
    "CsvDir",
    "CsvChunksDir",
    "CsvDirFile",
]
