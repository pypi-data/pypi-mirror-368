from typing import *
from abstract_utilities import make_list,get_media_exts, is_media_type
from dataclasses import dataclass, field
@dataclass
class ScanConfig:
    allowed_exts: Set[str]
    unallowed_exts: Set[str]
    exclude_types: Set[str]
    exclude_dirs: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
DEFAULT_ALLOWED_EXTS: Set[str] = {
    ".py", ".pyw",                             # python
    ".js", ".jsx", ".ts", ".tsx", ".mjs",      # JS/TS
    ".html", ".htm", ".xml",                   # markup
    ".css", ".scss", ".sass", ".less",         # styles
    ".json", ".yaml", ".yml", ".toml", ".ini",  # configs
    ".cfg", ".md", ".markdown", ".rst",        # docs
    ".sh", ".bash", ".env",                    # scripts/env
    ".txt"                                     # plain text
}

DEFAULT_EXCLUDE_TYPES: Set[str] = {
    "image", "video", "audio", "presentation",
    "spreadsheet", "archive", "executable"
}

# never want these—even if they sneak into ALLOWED
_unallowed = set(get_media_exts(DEFAULT_EXCLUDE_TYPES)) | {'.shp', '.cpg', '.dbf', '.shx','.geojson',".pyc",'.shx','.geojson','.prj','.sbn','.sbx'}
DEFAULT_UNALLOWED_EXTS = {e for e in _unallowed if e not in DEFAULT_ALLOWED_EXTS}

DEFAULT_EXCLUDE_DIRS: Set[str] = {
    "node_modules", "__pycache__", "backups", "backup"
}

DEFAULT_EXCLUDE_PATTERNS: Set[str] = {
    "__init__*", "*.tmp", "*.log", "*.lock", "*.zip","*~"
}

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

def define_defaults(
    allowed_exts: Optional[Set[str]] = None,
    unallowed_exts: Optional[Set[str]] = None,
    exclude_types: Optional[Set[str]] = None,
    exclude_dirs: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    add = False
    ):
    DEFAULT_CFG = ScanConfig(
        allowed_exts = get_default_modular(allowed_exts,default=DEFAULT_ALLOWED_EXTS,add=add,typ=set),
        unallowed_exts = get_default_modular(unallowed_exts,default=DEFAULT_UNALLOWED_EXTS,add=add,typ=set),
        exclude_types = get_default_modular(exclude_types,default=DEFAULT_EXCLUDE_TYPES,add=add,typ=set),
        exclude_dirs = get_default_modular(exclude_dirs,default=DEFAULT_EXCLUDE_DIRS,add=add,typ=list),
        exclude_patterns = get_default_modular(exclude_patterns,default=DEFAULT_EXCLUDE_PATTERNS,add=add,typ=list)
        )
    return DEFAULT_CFG
