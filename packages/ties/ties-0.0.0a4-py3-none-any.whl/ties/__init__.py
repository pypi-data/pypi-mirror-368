"""A CLI tool to duplicate and sync file content with advanced transformations."""

from ._file_processing import process_files
from .common_transforms import embed_environ

__all__ = ["embed_environ", "process_files"]
