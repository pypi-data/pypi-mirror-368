"""Documents resource wrapper."""

from functools import cache
import os
import shutil
import hashlib
from pathlib import Path

from dana.contrib.knows import Kpk
from dana.contrib.knows.core.fs import Dir

from .kpk import KpkResourceAgent

__all__ = ["doc_agent"]

@cache
def doc_agent(*docs_paths: Path | str) -> KpkResourceAgent:
    """Create local Knowledge Pack resource agent from documents."""
    # create empty Knowledge Pack with name being stable hash by sorting paths and using SHA-256
    paths_str = "|".join(sorted(os.path.abspath(p) for p in docs_paths))
    kpk_dir: Dir = Dir().sub_dir(hashlib.sha256(paths_str.encode()).hexdigest())

    (kpk_docs_path := kpk_dir.sub_path(Kpk.CONTENT_KEY, Kpk.DOCUMENTS_CONTENT_KEY)).mkdir(parents=True, exist_ok=True)

    # copy documents to Knowledge Pack's content
    for docs_path in docs_paths:
        dest_path: Path = kpk_docs_path / Path(docs_path).name  # use file names only to avoid path traversal issues
        shutil.copy2(src=docs_path, dst=dest_path, follow_symlinks=True)

    return KpkResourceAgent(path=kpk_dir.path)
