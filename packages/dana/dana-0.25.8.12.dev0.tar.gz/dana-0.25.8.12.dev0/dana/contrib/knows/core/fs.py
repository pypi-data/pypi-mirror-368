"""KNOWS file system utilities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import cached_property, reduce
import os
from pathlib import Path
from typing import ClassVar, Self

from fsspec.implementations.local import LocalFileSystem
from fsspec.spec import AbstractFileSystem
from adlfs import AzureBlobFileSystem, AzureDatalakeFileSystem
from gcsfs.core import GCSFileSystem
from s3fs.core import S3FileSystem

__all__ = [
    "PathOrStr",
    "Dir",
]

# remote file system protocol prefixes
_ADL_PROTOCOL_PREFIX: str = "adl://"
_BLOB_PROTOCOL_PREFIX: str = "blob://"
_GCS_PROTOCOL_PREFIX: str = "gcs://"
_S3_PROTOCOL_PREFIX: str = "s3://"

# Path or string-path type
type PathOrStr = Path | str

@dataclass
class Dir:
    """Local or remote directory."""

    LOCAL_CACHE_DIR_PATH: ClassVar[Path] = Path.home() / ".dana" / "knows" / "kb"

    path: PathOrStr = field(default=LOCAL_CACHE_DIR_PATH)

    def __post_init__(self):
        """Post-initialization: clean up path."""
        if isinstance(self.path, str):
            self.path: str = self.path.lstrip().rstrip(" /\\")
            if not self.on_remote_fs:
                self.path: Path = Path(self.path)

    def __eq__(self, other: Self) -> bool:
        """Check if two directories are equal."""
        return self.path == other.path

    @cached_property
    def on_adl(self) -> bool:
        """Check if directory is on Azure Datalake."""
        return isinstance(self.path, str) and self.path.startswith(_ADL_PROTOCOL_PREFIX)

    @cached_property
    def on_azure_blob(self) -> bool:
        """Check if directory is on Azure Blob."""
        return isinstance(self.path, str) and self.path.startswith(_BLOB_PROTOCOL_PREFIX)

    @cached_property
    def on_gcs(self) -> bool:
        """Check if directory is on GCS."""
        return isinstance(self.path, str) and self.path.startswith(_GCS_PROTOCOL_PREFIX)

    @cached_property
    def on_s3(self) -> bool:
        """Check if directory is on S3."""
        return isinstance(self.path, str) and self.path.startswith(_S3_PROTOCOL_PREFIX)

    @cached_property
    def on_remote_fs(self) -> bool:
        """Check if directory is on remote file system."""
        return self.on_adl or self.on_azure_blob or self.on_gcs or self.on_s3

    @cached_property
    def fs(self) -> AbstractFileSystem:
        """Get file system."""
        if isinstance(self.path, str):
            if self.path.startswith(_ADL_PROTOCOL_PREFIX):
                return AzureDatalakeFileSystem()

            if self.path.startswith(_BLOB_PROTOCOL_PREFIX):
                return AzureBlobFileSystem()

            if self.path.startswith(_GCS_PROTOCOL_PREFIX):
                return GCSFileSystem()

            if self.path.startswith(_S3_PROTOCOL_PREFIX):
                return S3FileSystem(key=os.environ.get("AWS_ACCESS_KEY_ID"),
                                    secret=os.environ.get("AWS_SECRET_ACCESS_KEY"))

        return LocalFileSystem(auto_mkdir=False,  # note: important for being recognized as default FS on Windows
                               use_listings_cache=False, listings_expiry_time=None, max_paths=None)

    @cached_property
    def exists(self) -> bool:
        """Check if directory exists."""
        return self.fs.isdir(path=self.path)

    @cached_property
    def local(self) -> Self:
        """Get local directory."""
        if self.on_remote_fs:
            local_dir_path: Path = self.LOCAL_CACHE_DIR_PATH / self.path.replace("://", os.path.sep).replace("/", os.path.sep)  # noqa: E501

            if self.on_adl:
                ...  # TODO: sync for Azure Datalake

            elif self.on_azure_blob:
                ...  # TODO: sync for Azure Blob

            elif self.on_gcs:
                ...  # TODO: sync for GCS

            elif self.on_s3:
                os.system(f"aws s3 sync {self.path} {local_dir_path} --delete --exact-timestamps")

            return Dir(path=local_dir_path)

        return self

    @cached_property
    def native_str_path(self) -> str:
        """Get path without protocol prefix (e.g., "gcs://", "s3://")."""
        return self.fs._strip_protocol(path=self.path)

    @property
    def ls(self) -> list[str]:
        """List of direct sub-directory and file names."""
        paths: list[str] = [path.rstrip(" /\\") for path in self.fs.ls(path=self.path, detail=False)]
        return [path.split(sep="/", maxsplit=-1)[-1]
                for path in paths if path != self.path]

    def sub_path(self, *sub_path_parts: PathOrStr) -> PathOrStr:
        """Build sub-path from current directory and sequence of sub-path parts."""
        return ("/".join([self.path] + [str(sub_path_part).replace("\\", "/") for sub_path_part in sub_path_parts])
                if self.on_remote_fs
                else reduce(lambda p, _p: p / str(_p).replace("/", os.path.sep), sub_path_parts, self.path))

    @property
    def direct_sub_dir_names(self) -> list[str]:
        """List of direct sub-directory names."""
        return [i for i in self.ls if self.fs.isdir(path=self.sub_path(i))]

    @property
    def direct_sub_paths(self) -> list[PathOrStr]:
        """List of direct sub-paths."""
        return [self.sub_path(i) for i in self.ls]

    def glob(self, pattern: str) -> Iterable[PathOrStr]:
        """Return sub-paths matching given pattern."""
        return (self.fs.glob(path=f'{self.path}/{pattern}', maxdepth=None)
                if self.on_remote_fs
                else self.path.glob(pattern=pattern, case_sensitive=True))

    def sub_dir(self, *sub_path_parts: PathOrStr) -> Self:
        """Get sub-directory from current directory and sequence of sub-path parts."""
        return Dir(path=self.sub_path(*sub_path_parts))

    @property
    def direct_sub_dirs(self) -> list[Self]:
        """List of direct sub-directories."""
        return [self.sub_dir(direct_sub_dir_name) for direct_sub_dir_name in self.direct_sub_dir_names]
