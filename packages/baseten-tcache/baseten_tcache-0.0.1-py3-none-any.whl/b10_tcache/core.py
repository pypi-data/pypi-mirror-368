"""
TODO(SRAY):
One thing I'm not sure about is:
1) what happens if b10fs is down? Will this implementation still work. Need to check...
"""

import os
import logging
import tempfile
import shutil
import uuid
import time
from pathlib import Path

from .environment import get_cache_filename, get_hostname
from .archive import create_archive, extract_archive, ArchiveError
from .utils import timed_fn


# Configuration
TORCH_CACHE_DIR = os.getenv("TORCH_CACHE_DIR", "/tmp/torchinductor_root")
B10FS_CACHE_DIR = os.getenv("B10FS_CACHE_DIR", "/cache/model/compile_cache")
LOCAL_WORK_DIR = os.getenv("LOCAL_WORK_DIR", "/app")
MAX_CACHE_SIZE_MB = int(os.getenv("MAX_CACHE_SIZE_MB", "1024"))

logger = logging.getLogger(__name__)


class CacheError(Exception):
    """Base cache operation error."""

    pass


@timed_fn(logger=logger, name="Loading compile cache")
def load_compile_cache() -> bool:
    """Load cache from b10fs using lock-free pattern."""
    b10fs_dir = Path(B10FS_CACHE_DIR)
    torch_dir = Path(TORCH_CACHE_DIR)
    work_dir = Path(LOCAL_WORK_DIR)

    try:
        cache_filename = get_cache_filename()
        cache_file = b10fs_dir / f"{cache_filename}.latest.tar.gz"
        logger.debug(f"Looking for cache file: {cache_file}")

        if not cache_file.exists():
            logger.info("No cache file found in b10fs")
            return False

        # Skip if already loaded
        if torch_dir.exists() and any(torch_dir.iterdir()):
            logger.info("Torch cache already loaded, skipping extraction")
            return True

        # Create temp local copy
        with tempfile.NamedTemporaryFile(
            suffix=".tar.gz", dir=work_dir, delete=False
        ) as f:
            temp_path = Path(f.name)
        logger.debug(f"Created temporary file for cache: {temp_path}")

        try:
            logger.info(
                f"Copying cache file from b10fs to local temp: {cache_file} -> {temp_path}"
            )
            shutil.copy2(cache_file, temp_path)
            logger.info(f"Extracting archive to torch cache dir: {torch_dir}")
            extract_archive(temp_path, torch_dir)
            logger.info("Cache extraction complete")
            return True
        finally:
            temp_path.unlink(missing_ok=True)
            logger.debug(f"Deleted temporary file: {temp_path}")

    except Exception as e:
        logger.debug(f"Load failed: {e}")
        return False


"""
What about the case in @b10-tcache/ where a single pod finishes an inference request,
and then the client calls save_compile_cache. And while we are creating the local archive,
another inference call on the same pod is kicked off, which then modifies the torch cache.
How would this be handled? Maybe just accept that the cache will be recompiled/overwritten?
Otherwise you'd need application level coordination to ensure that the cache is not modified
while we are creating the archive, but this doesn't really seem like a good idea in terms of adoption.
"""


@timed_fn(logger=logger, name="Saving compile cache")
def save_compile_cache() -> bool:
    """Save cache using the journal pattern."""
    b10fs_dir = Path(B10FS_CACHE_DIR)
    torch_dir = Path(TORCH_CACHE_DIR)
    work_dir = Path(LOCAL_WORK_DIR)

    try:
        # Check if anything to save
        if not torch_dir.exists() or not any(torch_dir.iterdir()):
            logger.info("No torch cache to save")
            return False

        cache_filename = get_cache_filename()
        hostname = get_hostname()
        final_file = b10fs_dir / f"{cache_filename}.latest.tar.gz"
        temp_file = b10fs_dir / f"{cache_filename}.{hostname}.incomplete.tar.gz"

        with tempfile.NamedTemporaryFile(
            suffix=".tar.gz", dir=work_dir, delete=False
        ) as f:
            local_temp = Path(f.name)
        logger.debug(f"Created local temp file for archive: {local_temp}")

        try:
            create_archive(torch_dir, local_temp, MAX_CACHE_SIZE_MB)

            b10fs_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Copying archive to b10fs: {local_temp} -> {temp_file}")
            shutil.copy2(local_temp, temp_file)

            logger.info(
                f"Renaming temp file to final cache file: {temp_file} -> {final_file}"
            )
            temp_file.rename(final_file)

            logger.info("Cache save complete")
            return True

        finally:
            local_temp.unlink(missing_ok=True)
            temp_file.unlink(missing_ok=True)  # Cleanup if rename failed
            logger.debug(f"Cleaned up temp files: {local_temp}, {temp_file}")

    except Exception as e:
        logger.debug(f"Save failed: {e}")
        return False


def clear_local_cache() -> bool:
    """Clear local torch cache."""
    torch_dir = Path(TORCH_CACHE_DIR)

    try:
        if not torch_dir.exists():
            return True

        shutil.rmtree(torch_dir)
        return True

    except Exception as e:
        logger.debug(f"Clear failed: {e}")
        return False
