from pathlib import Path
from giv.commands.base import BaseCommand

class ClearCacheCommand(BaseCommand):
    """Command to clear all cache files."""
    name = "clear-cache"
    description = "Clear all cached summaries and metadata."

    def run(self):
        cache_dir = Path.cwd() / ".giv" / "cache"
        if cache_dir.exists():
            for file in cache_dir.glob("*"):
                file.unlink()
            print("Cache cleared.")
        else:
            print("No cache directory found.")
        # Also clear in-memory metadata cache
        try:
            from giv.lib.metadata import MetadataManager
            MetadataManager.clear_cache()
        except Exception:
            pass
        return 0
