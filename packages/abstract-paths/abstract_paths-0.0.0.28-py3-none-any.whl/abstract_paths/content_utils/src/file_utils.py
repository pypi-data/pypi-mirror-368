import os
import glob
from typing import Optional, Union, List, Dict
from collections import defaultdict

def normalize_paths(paths: Optional[Union[bool, str]] = True) -> str:
    """
    Normalize the paths parameter for glob pattern.
    
    - If True, returns '**' for recursive search.
    - If False or None, returns '_' (non-recursive placeholder).
    - If str, returns the provided string.
    
    Args:
        paths: The paths specification.
    
    Returns:
        Normalized paths string.
    """
    if paths is True:
        return '**'
    elif paths in (False, None):
        return '_'
    elif isinstance(paths, str):
        return paths
    raise ValueError(f"Invalid paths value: {paths}")

def normalize_extensions(exts: Optional[Union[bool, str, List[str]]] = True) -> str:
    """
    Normalize the extensions parameter for glob pattern.
    
    - If True, returns '*' for all files.
    - If False or None, returns '_' (no extension filter).
    - If str starting with '.', returns '*{exts}'.
    - If str without '.', assumes it's the extension and adds '.'.
    - If list of str, returns '*.' + '{ext1,ext2,...}' for multiple extensions.
    
    Args:
        exts: The extensions specification.
    
    Returns:
        Normalized extensions string.
    """
    if exts is True:
        return '*'
    elif exts in (False, None):
        return '_'
    elif isinstance(exts, str):
        if exts.startswith('.'):
            return f"*{exts}"
        else:
            return f"*.{exts}"
    elif isinstance(exts, list):
        if not exts:
            return '*'
        normalized = [e.lstrip('.') for e in exts]
        return "*." + "{" + ",".join(normalized) + "}"
    raise ValueError(f"Invalid exts value: {exts}")

def build_glob_pattern(
    directory: str,
    paths: Optional[Union[bool, str]] = True,
    exts: Optional[Union[bool, str, List[str]]] = True
) -> str:
    """
    Build the full glob search pattern by joining directory, paths, and extensions.
    
    Args:
        directory: The base directory to search in.
        paths: The paths specification (see normalize_paths).
        exts: The extensions specification (see normalize_extensions).
    
    Returns:
        The complete glob pattern string.
    """
    norm_paths = normalize_paths(paths)
    norm_exts = normalize_extensions(exts)
    return os.path.join(directory, norm_paths, norm_exts)

def findGlobFiles(
    directory: str,
    paths: Optional[Union[bool, str]] = True,
    exts: Optional[Union[bool, str, List[str]]] = True,
    recursive: bool = True
) -> List[str]:
    """
    Find files in the directory using glob based on the provided patterns.
    
    This is the main entry point for file searching. It builds the glob pattern
    and performs the search.
    
    Args:
        directory: The base directory to search in.
        paths: The paths specification (see normalize_paths).
        exts: The extensions specification (see normalize_extensions).
        recursive: Whether to search recursively (affects glob behavior).
    
    Returns:
        List of matching file paths.
    """
    search_pattern = build_glob_pattern(directory, paths, exts)
    return glob.glob(search_pattern, recursive=recursive)
def get_e_normalized(f,exts):
    norm_exts = normalize_extensions(exts)
    if norm_exts == '_':
        return True
    norm_exts_spl = norm_exts.lstrip('*').split(',')
    lstrip_exts = [norm_exts.lstrip('*.')]
    brak_in_exts = '{' in norm_exts
    def get_strip(f,e,norm_exts_spl,lstrip_exts,brak_in_exts):
        if brak_in_exts:
            f.endswith(e.lstrip('*.'))
        return lstrip_exts
    if any(get_strip(f,e,norm_exts_spl,lstrip_exts,brak_in_exts) for e in norm_exts_spl):
         return True
    return False
def build_directory_tree(
    directory: str,
    paths: Optional[Union[bool, str]] = True,
    exts: Optional[Union[bool, str, List[str]]] = True,
    recursive: bool = True,
    include_files: bool = True,
    prefix: str = ""
) -> str:
    """
    Generate a text-based tree map of the directory structure.
    
    This function uses os.walk to traverse the directory and builds a 
    printable tree string that represents the hierarchy. It can filter 
    files based on extensions if provided. The output is designed to be 
    easily copied to the clipboard for quick inspection of the dir structure.
    
    Args:
        directory: The base directory to map.
        paths: The paths specification (influences recursion if not True).
        exts: The extensions to include (if include_files=True).
        recursive: Whether to traverse recursively.
        include_files: Whether to include files in the tree (True) or just dirs (False).
        prefix: Internal prefix for indentation in recursive calls.
    
    Returns:
        A string representation of the directory tree.
    """
    tree_str = []
    directory = os.path.abspath(directory)
    base_name = os.path.basename(directory)
    tree_str.append(f"{prefix}{base_name}/")
    
    if not recursive:
        # Non-recursive: just list immediate contents
        contents = os.listdir(directory)
        dirs = [d for d in contents if os.path.isdir(os.path.join(directory, d))]
        files = [f for f in contents if os.path.isfile(os.path.join(directory, f))]
        
        for i, d in enumerate(sorted(dirs)):
            is_last = (i == len(dirs) - 1) and not files
            tree_str.append(f"{prefix}{'└── ' if is_last else '├── '}{d}/")
        
        if include_files:
            norm_exts = normalize_extensions(exts).lstrip('*')  # For simple filtering
            for i, f in enumerate(sorted(files)):
                if norm_exts != '_' and not f.endswith(tuple(norm_exts.split(',')) if '{' in norm_exts else (norm_exts,)):
                    continue
                is_last = (i == len(files) - 1)
                tree_str.append(f"{prefix}{'└── ' if is_last else '├── '}{f}")
    else:
        # Recursive: use os.walk
        file_list = findGlobFiles(directory, paths, exts, recursive=True) if include_files else []
        dir_structure: Dict[str, List[str]] = defaultdict(list)
        
        # Build dir -> subdirs/files mapping
        for root, dirs, files in os.walk(directory):
            rel_root = os.path.relpath(root, directory)
            if rel_root != '.':
                parent = os.path.dirname(rel_root)
                dir_structure[parent].append(os.path.basename(rel_root) + '/')
            
            if include_files:
                filtered_files = [f for f in files if get_e_normalized(f,exts)]
                dir_structure[rel_root].extend(filtered_files)
        if normalize_extensions(exts) == '_':
            return True
        
        
        # Recursive tree builder
        def _build_tree(current: str, prefix: str, structure: Dict[str, List[str]]) -> List[str]:
            lines = []
            contents = sorted(structure.get(current, []))
            for i, item in enumerate(contents):
                is_last = (i == len(contents) - 1)
                new_prefix = prefix + ('    ' if is_last else '│   ')
                connector = '└── ' if is_last else '├── '
                
                lines.append(f"{prefix}{connector}{item}")
                
                if item.endswith('/'):
                    sub_path = os.path.join(current, item.rstrip('/')) if current != '.' else item.rstrip('/')
                    lines.extend(_build_tree(sub_path, new_prefix, structure))
            return lines
        
        tree_str.extend(_build_tree('.', prefix + '│   ', dir_structure))
    
    return '\n'.join(tree_str)

def get_directory_map(
    directory: str,
    paths: Optional[Union[bool, str]] = True,
    exts: Optional[Union[bool, str, List[str]]] = True,
    recursive: bool = True,
    include_files: bool = True
) -> str:
    """
    Public entry point to get a copyable directory map string.
    
    This wraps build_directory_tree to provide a simple API for generating
    and returning the tree string, which can be printed or copied to clipboard.
    
    Example usage:
    map_str = get_directory_map('/path/to/dir')
    print(map_str)  # Or copy to clipboard via pyperclip or similar
    
    Args:
        directory: The base directory to map.
        paths: The paths specification.
        exts: The extensions to include.
        recursive: Whether to map recursively.
        include_files: Whether to include files in the map.
    
    Returns:
        The directory tree as a string.
    """
    return build_directory_tree(directory, paths, exts, recursive, include_files)

