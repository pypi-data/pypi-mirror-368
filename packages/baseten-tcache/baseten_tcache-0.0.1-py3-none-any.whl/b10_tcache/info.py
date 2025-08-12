import logging
from pathlib import Path
from typing import Dict, Any

from .environment import get_cache_filename, get_environment_key
from .archive import get_file_size_mb
from .core import TORCH_CACHE_DIR, B10FS_CACHE_DIR, MAX_CACHE_SIZE_MB

logger = logging.getLogger(__name__)


def get_cache_info() -> Dict[str, Any]:
    """Get current cache state information."""
    torch_dir = Path(TORCH_CACHE_DIR)
    b10fs_dir = Path(B10FS_CACHE_DIR)
    cache_filename = get_cache_filename()
    cache_file = b10fs_dir / f"{cache_filename}.latest.tar.gz"

    info = {
        "environment_key": get_environment_key(),
        "local_cache_exists": torch_dir.exists() and any(torch_dir.iterdir()),
        "b10fs_cache_exists": cache_file.exists(),
    }

    # Add size info
    if info["local_cache_exists"]:
        try:
            # FIXME(SR): I guess directory structure could change here while rglob is running/iterating, so this is not safe.
            # But this is for debuggging anyways, we can remove/revisit this later. Not critical imho.
            local_size = sum(
                f.stat().st_size for f in torch_dir.rglob("*") if f.is_file()
            )
            info["local_cache_size_mb"] = local_size / (1024 * 1024)
        except Exception:
            info["local_cache_size_mb"] = None

    if info["b10fs_cache_exists"]:
        info["b10fs_cache_size_mb"] = get_file_size_mb(cache_file)

    return info


def list_available_caches() -> Dict[str, Any]:
    """List all available cache files."""
    b10fs_dir = Path(B10FS_CACHE_DIR)

    if not b10fs_dir.exists():
        return {"caches": [], "current_environment": get_environment_key()}

    caches = []

    # Find all latest cache files
    for cache_file in b10fs_dir.glob("cache_*.latest.tar.gz"):
        try:
            # Extract env key: cache_a1b2c3d4e5f6.latest.tar.gz
            env_key = cache_file.name.replace("cache_", "").replace(
                ".latest.tar.gz", ""
            )

            cache_info = {
                "filename": cache_file.name,
                "environment_key": env_key,
                "size_mb": get_file_size_mb(cache_file),
                "is_current_environment": env_key == get_environment_key(),
                "created_time": cache_file.stat().st_mtime,
            }

            caches.append(cache_info)

        except Exception as e:
            logger.debug(f"Error reading cache file {cache_file}: {e}")

    # Sort by creation time (newest first)
    caches.sort(key=lambda x: x["created_time"], reverse=True)

    return {
        "caches": caches,
        "current_environment": get_environment_key(),
        "total_caches": len(caches),
        "current_cache_exists": any(c["is_current_environment"] for c in caches),
    }
