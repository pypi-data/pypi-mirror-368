import os
import time
import threading

class Cache:
    __slots__ = ('_data', '_times', '_lock')

    def __init__(self):
        self._data = {}   # path -> (translated_source, mtime)
        self._times = {}  # path -> last_access_time (epoch)
        self._lock = threading.RLock()

    def get(self, path, tokenizer):
        """
        Return translated source for path, caching results.
        Returns None on failure.
        """
        with self._lock:
            try:
                stat = os.stat(path)
                mtime = stat.st_mtime

                # Check cache hit with mtime validation
                if path in self._data:
                    cached_source, cached_mtime = self._data[path]
                    if cached_mtime == mtime:
                        self._times[path] = time.time()
                        return cached_source

                # Read and translate
                with open(path, 'r', encoding='utf-8') as f:
                    source = f.read()

                translated = tokenizer.translate_source(source)

                # Update caches
                self._data[path] = (translated, mtime)
                self._times[path] = time.time()

                # Evict oldest entries if cache too large
                if len(self._data) > 128:
                    self._evict()

                return translated

            except (OSError, UnicodeDecodeError):
                return None

    def _evict(self):
        """
        Evict oldest 25% of cache entries by last access time.
        """
        with self._lock:
            to_remove = max(1, len(self._data) // 4)
            oldest = sorted(self._times.items(), key=lambda x: x[1])[:to_remove]
            for path, _ in oldest:
                self._data.pop(path, None)
                self._times.pop(path, None)

    def clear(self):
        """Clear all cached data."""
        with self._lock:
            self._data.clear()
            self._times.clear()


# Global instance
_cache = Cache()

def get_cache():
    return _cache
