# file_reader.py

import os,glob
import fnmatch
from pathlib import Path
from typing import List, Optional, Set

from abstract_utilities import make_list,get_media_exts, is_media_type
def get_allowed(allowed=None):
    if allowed != False:
        if allowed == True:
            allowed = None
        allowed = allowed or make_allowed_predicate()
    else:
        def allowed(*args):
            return True
        allowed = allowed
    return allowed
def get_globs(items):
    glob_paths = []
    for item in make_list(items):
        pattern = os.path.join(item, "**/*")  # include all files recursively\n
        glob_paths += glob.glob(pattern, recursive=True)
    return glob_paths
def get_files(items,allowed=True):
    allowed = get_allowed(allowed=allowed)
    return [item for item in items if item and os.path.isfile(item) and allowed(item)]
def get_dirs(items,allowed=False):
    allowed = get_allowed(allowed=allowed)
    return [item for item in items if item and os.path.isdir(item) and allowed(item)]
def filter_files(items,allowed=None,files = []):
    allowed = get_allowed(allowed=allowed)
    glob_paths = get_globs(items)
    return [glob_path for glob_path in glob_paths if glob_path and os.path.isfile(glob_path) and glob_path not in files and allowed(glob_path)]
def filter_dirs(items,allowed=None,dirs = []):
    allowed = get_allowed(allowed=allowed)
    glob_paths = get_globs(items)
    return [glob_path for glob_path in glob_paths if glob_path and os.path.isdir(glob_path) and glob_path not in dirs and allowed(glob_path)]
def get_all_files(items,allowed=None):
    dirs = get_all_dirs(items)
    files = get_files(items)
    nu_files = []
    for directory in dirs:
        files += filter_files(directory,allowed=allowed,files=files)
    return files
def get_all_dirs(items,allowed=None):
    allowed = get_allowed(allowed=allowed)
    dirs = get_dirs(items)
    nu_dirs=[]
    for directory in dirs:
        nu_dirs += filter_dirs(directory,allowed=allowed,dirs=nu_dirs)
    return nu_dirs
# ─── your global defaults ────────────────────────────────────────────────────
DEFAULT_ALLOWED_EXTS: Set[str] = {".ts", ".tsx", ".js", ".jsx", ".mts", ".cts"}

DEFAULT_EXCLUDE_TYPES: Set[str] = {
    "image", "video", "audio", "presentation",
    "spreadsheet", "archive", "executable"
}

# never want these—even if they sneak into ALLOWED
_unallowed = set(get_media_exts(DEFAULT_EXCLUDE_TYPES)) | {'.shp', '.cpg', '.dbf', '.shx','.geojson',".pyc",'.shx','.geojson','.prj','.sbn','.sbx'}
DEFAULT_UNALLOWED_EXTS = {e for e in _unallowed if e not in DEFAULT_ALLOWED_EXTS}

DEFAULT_EXCLUDE_DIRS: Set[str] = {
    "node_modules", "__pycache__", "backups", "backup","junk"
}

DEFAULT_EXCLUDE_PATTERNS: Set[str] = {
    "__init__*", "*.tmp", "*.log", "*.lock", "*.zip","*~"
}
# ─── 1) Build a predicate from user + defaults ──────────────────────────────

def get_default_modular(obj,default=None,add=False,typ=set):
    if obj in [False,True,None]:
        if obj in [True,None]:
            obj = default
        if obj == False:
            obj =None
    elif add == True:
        if typ == set:
            obj = typ(typ(obj) | typ(default))
        elif typ == list:
            obj = make_list(obj) + make_list(default)
    return obj
def make_allowed_predicate(
    *,
    allowed_exts: Optional[Set[str]] = None,
    unallowed_exts: Optional[Set[str]] = None,
    exclude_types: Optional[Set[str]] = None,
    exclude_dirs: Optional[List[str]] = None,
    extra_patterns: Optional[List[str]] = None,
    add = False
) -> callable:
    allowed_exts = get_default_modular(allowed_exts,default=DEFAULT_ALLOWED_EXTS,add=add,typ=set)
    unallowed_exts = get_default_modular(unallowed_exts,default=DEFAULT_UNALLOWED_EXTS,add=add,typ=set)
    exclude_types = get_default_modular(exclude_types,default=DEFAULT_EXCLUDE_TYPES,add=add,typ=set)
    exclude_dirs = get_default_modular(exclude_dirs,default=DEFAULT_EXCLUDE_DIRS,add=add,typ=list)
    patterns_to_skip = get_default_modular(extra_patterns,default=DEFAULT_EXCLUDE_PATTERNS,add=add,typ=list)

    def allowed(path: str) -> bool:
        p = Path(path)
        name = p.name.lower()
        path_str = str(p).lower()
        # A) Skip directories by substring or pattern
        for dir_pattern in exclude_dirs:
            if p.is_dir() and (dir_pattern in path_str or fnmatch.fnmatch(name, dir_pattern.lower())):
                return False
        # B) Skip by filename pattern
        for pat in patterns_to_skip:
            if fnmatch.fnmatch(name, pat.lower()):
                return False
        # C) Skip by media category
        if p.is_file():
            ext = p.suffix.lower()
            if ext not in allowed_exts or ext in unallowed_exts:
                return False
        return True
    return allowed

def collect_filepaths(
    roots: List[str],
    *,
    allowed_exts: Set[str] = None,
    unallowed_exts: Set[str] = None,
    exclude_types: Set[str] = None,
    exclude_dirs: List[str] = None,
    exclude_file_patterns: List[str] = None,
) -> List[str]:
    allowed = make_allowed_predicate(
        allowed_exts=allowed_exts,
        unallowed_exts=unallowed_exts,
        exclude_types=exclude_types,
        exclude_dirs=exclude_dirs,
        extra_patterns=exclude_file_patterns
    )
    roots = make_list(roots or [])
    original_dirs = get_dirs(roots, allowed=allowed)
    original_globs = get_globs(original_dirs)
    files = get_files(original_globs, allowed=allowed)
    filtered_dirs = filter_dirs(original_dirs, allowed=allowed)
    for filtered_directory in filtered_dirs:
        files += filter_files(filtered_directory, allowed=allowed, files=files)
    return files
