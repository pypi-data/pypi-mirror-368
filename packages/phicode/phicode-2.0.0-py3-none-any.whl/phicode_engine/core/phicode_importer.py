import importlib.abc
import importlib.util
import sys
import os
import marshal
import struct
import hashlib
from pathlib import Path
from functools import lru_cache
from threading import Lock

from ..map.tokenizer import Tokenizer
from .cache import get_cache

class PhicodeLoader(importlib.abc.Loader):
    __slots__ = ('path', '_cache', '_tokenizer', '_bytecode_dir')

    def __init__(self, path):
        self.path = path
        self._cache = get_cache()
        self._tokenizer = Tokenizer()
        self._bytecode_dir = Path.home() / '.phicode_cache'
        self._bytecode_dir.mkdir(exist_ok=True)

    def _bytecode_path(self):
        """Generate cache file path based on SHA256 hash of source path."""
        hash_digest = hashlib.sha256(self.path.encode('utf-8')).hexdigest()
        filename = f"{hash_digest[:16]}.pyc"
        return self._bytecode_dir / filename

    def _load_bytecode(self):
        try:
            cache_path = self._bytecode_path()
            if not cache_path.exists():
                return None

            source_stat = os.stat(self.path)
            cache_stat = os.stat(cache_path)

            # Cache must be newer than source
            if cache_stat.st_mtime < source_stat.st_mtime:
                return None

            with open(cache_path, 'rb') as f:
                magic = f.read(4)
                if magic != importlib.util.MAGIC_NUMBER:
                    return None

                f.read(8)  # flags + timestamp
                size_bytes = f.read(4)
                if len(size_bytes) != 4:
                    return None
                size = struct.unpack('<I', size_bytes)[0]

                bytecode = f.read()
                if len(bytecode) == size:
                    return bytecode
        except (OSError, struct.error):
            pass
        return None

    def _save_bytecode(self, bytecode):
        try:
            cache_path = self._bytecode_path()
            source_stat = os.stat(self.path)

            with open(cache_path, 'wb') as f:
                f.write(importlib.util.MAGIC_NUMBER)
                f.write(struct.pack('<I', 0))  # flags
                f.write(struct.pack('<I', int(source_stat.st_mtime)))
                f.write(struct.pack('<I', len(bytecode)))
                f.write(bytecode)
        except (OSError, struct.error):
            pass

    def create_module(self, spec):
        return None  # Default module creation

    def exec_module(self, module):
        # Try cached bytecode first
        cached_bytecode = self._load_bytecode()
        if cached_bytecode:
            try:
                code = marshal.loads(cached_bytecode)
                exec(code, module.__dict__)
                return
            except (ValueError, marshal.UnmarshalError, TypeError):
                pass  # fallback to recompile

        # Get PHICODE source translated to Python source
        source = self._cache.get(self.path, self._tokenizer)
        if source is None:
            raise ImportError(f"Cannot read or translate source: {self.path}")

        try:
            code = compile(source, self.path, 'exec', optimize=2)
            try:
                bytecode = marshal.dumps(code)
                self._save_bytecode(bytecode)
            except Exception:
                pass
            exec(code, module.__dict__)
        except SyntaxError as e:
            raise ImportError(f"Syntax error in {self.path}: {e}")

class PhicodeFinder(importlib.abc.MetaPathFinder):
    __slots__ = ('base_path', '_negative_cache', '_lock')

    def __init__(self, base_path):
        self.base_path = os.path.abspath(base_path)
        self._negative_cache = set()
        self._lock = Lock()

    @lru_cache(maxsize=256)
    def _find_file(self, fullname):
        """
        Locate .φ file or package __init__.φ for the module fullname.
        Returns (filepath, is_package) or (None, False)
        """
        parts = fullname.split('.')

        # Check module file
        module_path = os.path.join(self.base_path, *parts) + '.φ'
        if os.path.isfile(module_path):
            return module_path, False

        # Check package directory
        package_dir = os.path.join(self.base_path, *parts)
        init_file = os.path.join(package_dir, '__init__.φ')
        if os.path.isfile(init_file):
            return init_file, True

        return None, False

    def find_spec(self, fullname, path, target=None):
        # Check negative cache thread-safely
        with self._lock:
            if fullname in self._negative_cache:
                return None

        file_path, is_package = self._find_file(fullname)
        if file_path:
            loader = PhicodeLoader(file_path)
            submodule_locations = [os.path.dirname(file_path)] if is_package else None
            spec = importlib.util.spec_from_file_location(
                fullname,
                file_path,
                loader=loader,
                submodule_search_locations=submodule_locations
            )
            return spec
        else:
            # Update negative cache
            with self._lock:
                self._negative_cache.add(fullname)
            return None


def install_phicode_importer(base_path: str):
    finder = PhicodeFinder(base_path)
    sys.meta_path.insert(0, finder)
