from __future__ import annotations
import sys, re, ast, pathspec, json, os, time
from pathlib import Path
import importlib.util
import sysconfig
from typing import Union, Any, Set, List, Dict, Optional, overload
from ast import literal_eval
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
from noexcept import no
from .pathFinder import *
from .errorCodes import ErrorCodes

# Pre-compiled regex patterns for performance
VERSION_SPECIFIER_PATTERN = re.compile(r'[<>=!~;]')
FIELD_ASSIGNMENT_PATTERN_CACHE = {}

# Module-level caches
_AST_CACHE: Dict[str, tuple] = {}  # {file_path: (mtime, dependencies)}
_FILE_CONTENT_CACHE: Dict[str, tuple] = {}  # {file_path: (mtime, content)}
_DIRECTORY_CACHE: Dict[str, tuple] = {}  # {dir_path: (mtime, file_list)}
_STDLIB_PATHS_CACHE = None
_MODULE_SETTINGS_CACHE = None
_MODULE_SETTINGS_MTIME = 0

def _loadModuleSettings() -> Dict[str, Any]:
    """Load module-level settings with caching."""
    global _MODULE_SETTINGS_CACHE, _MODULE_SETTINGS_MTIME
    
    config_path = Path(__file__).parent.parent / "config" / "module_settings.json"
    if not config_path.exists():
        no(ErrorCodes.CONFIG_NOT_FOUND, f"Module settings not found at {config_path}", soften=True)
        return {"common_aliases": {}, "performance": {"max_parallel_processes": 4, "enable_parallel_processing": True}}
    
    current_mtime = config_path.stat().st_mtime
    if _MODULE_SETTINGS_CACHE is None or current_mtime > _MODULE_SETTINGS_MTIME:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                _MODULE_SETTINGS_CACHE = json.load(f)
            _MODULE_SETTINGS_MTIME = current_mtime
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            no(ErrorCodes.CONFIG_PARSE_ERROR, f"Failed to parse module settings: {e}", soften=True)
            return {"common_aliases": {}, "performance": {"max_parallel_processes": 4, "enable_parallel_processing": True}}
        except (OSError, PermissionError) as e:
            no(ErrorCodes.FILE_READ_ERROR, f"Cannot read module settings: {e}", soften=True)
            return {"common_aliases": {}, "performance": {"max_parallel_processes": 4, "enable_parallel_processing": True}}
    
    return _MODULE_SETTINGS_CACHE

def _getStdlibPaths() -> Dict[str, str]:
    """Get and cache standard library paths."""
    global _STDLIB_PATHS_CACHE
    if _STDLIB_PATHS_CACHE is None:
        _STDLIB_PATHS_CACHE = sysconfig.get_paths()
    return _STDLIB_PATHS_CACHE

def _getCachedFileContent(file_path: Path) -> Optional[str]:
    """Get file content with caching based on modification time."""
    file_path_str = str(file_path.resolve())
    current_mtime = file_path.stat().st_mtime
    
    if file_path_str in _FILE_CONTENT_CACHE:
        cached_mtime, cached_content = _FILE_CONTENT_CACHE[file_path_str]
        if cached_mtime >= current_mtime:
            return cached_content
    
    try:
        content = file_path.read_text(encoding="utf-8")
        _FILE_CONTENT_CACHE[file_path_str] = (current_mtime, content)
        return content
    except Exception:
        return None

def _processFileForDependencies(file_path: Path) -> Set[str]:
    """Worker function for parallel processing of individual files."""
    try:
        return set(getFileDependencies(file_path))
    except Exception:
        return set()

def getProjectDependencies(filePaths: List[Path], debug: bool = False) -> Set[str]:
    """
    Extract dependencies from Python files with parallel processing and caching.
    """
    dependencies: Set[str] = set()
    projectModules: Set[str] = {(p.parent.name if p.name == "__init__.py" else p.stem) for p in filePaths}
    
    # Filter to only Python files that exist
    pythonFiles = [f for f in filePaths if f.is_file() and f.suffix == ".py"]
    
    if not pythonFiles:
        return dependencies
    
    # Check if parallel processing is enabled
    moduleSettings = _loadModuleSettings()
    useParallel = moduleSettings.get("performance", {}).get("enable_parallel_processing", True)
    maxWorkers = min(
        moduleSettings.get("performance", {}).get("max_parallel_processes", 4),
        cpu_count(),
        len(pythonFiles)
    )
    
    if useParallel and len(pythonFiles) > 1 and maxWorkers > 1:
        # Use parallel processing for multiple files
        with ThreadPoolExecutor(max_workers=maxWorkers) as executor:
            futureToFile = {executor.submit(_processFileForDependencies, file): file for file in pythonFiles}
            
            for future in as_completed(futureToFile):
                file = futureToFile[future]
                try:
                    detected = future.result()
                    
                    if debug:
                        print(f"[DEBUG] {file}: raw detected imports = {sorted(detected)}")
                    
                    # Strip out stdlib modules
                    detected = {m for m in detected if not isPythonPackage(m)}
                    
                    if debug:
                        print(f"[DEBUG] {file}: third-party imports = {sorted(detected)}")
                    
                    # Strip out any internal references
                    detected = {m for m in detected if m not in projectModules}
                    
                    if debug:
                        print(f"[DEBUG] {file}: external imports = {sorted(detected)}")
                    
                    dependencies.update(detected)
                    
                except Exception as e:
                    if debug:
                        print(f"[DEBUG] Error processing {file}: {e}")
    else:
        # Sequential processing for small numbers of files or when disabled
        for file in pythonFiles:
            detected: Set[str] = set(getFileDependencies(file))

            if debug:
                print(f"[DEBUG] {file}: raw detected imports = {sorted(detected)}")

            # Strip out stdlib modules
            detected = {m for m in detected if not isPythonPackage(m)}
            
            if debug:
                print(f"[DEBUG] {file}: third-party imports = {sorted(detected)}")

            # Strip out any internal references
            detected = {m for m in detected if m not in projectModules}

            if debug:
                print(f"[DEBUG] {file}: external imports = {sorted(detected)}")
                            
            dependencies.update(detected)

    if debug:
        print("Dependency installation check complete.")

    return dependencies

def mod(
        path: Union[str, Path], 
        field: str, 
        new_value: Union[str, bool, int, float, list, dict, None],
        *,
        debug: bool = False
        ) -> None:
    """
    Replace the Python literal assigned to `field` with the raw text in `new_value`,
    matching it anywhere in the file—inline, on its own line, even across multiple lines.
    `new_value` must be the exact literal (e.g. "['a','b']", "{'x':1}", "42", etc.).
    """
    path = Path(path)
    
    # Use cached file content
    text = _getCachedFileContent(path)
    if text is None:
        text = path.read_text(encoding="utf-8")

    # Cache compiled patterns for reuse
    if field not in FIELD_ASSIGNMENT_PATTERN_CACHE:
        # Build a pattern for ANY simple literal: list, dict, tuple, string, number, bool, None
        value_pattern = (
            r'\[.*?\]'                  # list [...]
          r'|\{.*?\}'                   # dict {...}
          r'|\(.*?\)'                   # tuple (...)
          r'|"(?:\\.|[^"\\])*"'         # double-quoted string
          r"|'(?:\\.|[^'\\])*'"         # single-quoted string
          r'|\b(?:True|False|None)\b'   # booleans & None
          r'|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'  # int/float/scientific
        )

        FIELD_ASSIGNMENT_PATTERN_CACHE[field] = re.compile(
            # 1) prefix:   the field name, optional spaces, =, optional spaces
            rf'(?P<prefix>{re.escape(field)}\s*=\s*)'
            # 2) old:      whatever literal was there
            rf'(?P<old>{value_pattern})'
            # 3) suffix:   optional whitespace + optional semicolon
            r'(?P<suffix>\s*;?)',
            flags=re.MULTILINE | re.DOTALL
        )
    
    pattern = FIELD_ASSIGNMENT_PATTERN_CACHE[field]

    def _repl(m: re.Match) -> str:
        if debug: print("Replacing %r: %r → %r", field, m.group("old"), new_value)
        # re-insert exactly the prefix, then our new_value, then exactly the suffix
        return f"{m.group('prefix')}{new_value}{m.group('suffix')}"

    new_text, count = pattern.subn(_repl, text, count=1)
    if count != 1:
        raise RuntimeError(f"No assignment to `{field}` found in {path!r}")
    
    path.write_text(new_text, encoding="utf-8")
    
    # Invalidate cache since file was modified
    file_path_str = str(path.resolve())
    if file_path_str in _FILE_CONTENT_CACHE:
        del _FILE_CONTENT_CACHE[file_path_str]
    
    if debug: print("Field %r updated in %s", field, path)

@lru_cache(maxsize=256)
def getParam(path: Union[str, Path], field: str, default: Any = None) -> Any:
    """
    Read the file at `path` and return the Python-evaluated value of the assignment
    to `field`.  Supports lists, dicts, tuples (single- or multi-line), strings,
    booleans, None, and numeric literals.
    """
    path = Path(path)
    
    # Use cached file content
    text = _getCachedFileContent(path)
    if text is None:
        if not path.exists():
            return default
        text = path.read_text(encoding="utf-8")

    # Cache pattern compilation based on field
    pattern_key = f"getParam_{field}"
    if pattern_key not in FIELD_ASSIGNMENT_PATTERN_CACHE:
        # Build a combined regex for the "value":
        value_pattern = (
            r'\[.*?\]'
            r'|\{.*?\}'
            r'|\(.*?\)'
            r'|"(?:\\.|[^"\\])*"'
            r"|'(?:\\.|[^'\\])*'"
            r'|\b(?:True|False|None)\b'
            r'|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
        )

        FIELD_ASSIGNMENT_PATTERN_CACHE[pattern_key] = re.compile(
            rf'(?P<prefix>{re.escape(field)}\s*=\s*)'
            rf'(?P<value>{value_pattern})'
            r'(?P<suffix>\s*;?)',
            flags=re.MULTILINE | re.DOTALL
        )
    
    pattern = FIELD_ASSIGNMENT_PATTERN_CACHE[pattern_key]
    m = pattern.search(text)
    if not m:
        return default

    raw = m.group("value")
    try:
        # literal_eval covers lists, dicts, tuples, strings, booleans, None, numbers
        return literal_eval(raw)
    except Exception:
        # As a last resort, return the raw text
        return raw
        
def getFileDependencies(path: Union[str, Path]) -> List[str]:
    """
    Parse the Python file at `path` and return a sorted list of all
    top-level module names that are imported anywhere in it.
    Uses caching based on file modification time.
    """
    path = Path(path)
    file_path_str = str(path.resolve())
    
    try:
        current_mtime = path.stat().st_mtime
    except (OSError, FileNotFoundError):
        return []
    
    # Check cache first
    if file_path_str in _AST_CACHE:
        cached_mtime, cached_deps = _AST_CACHE[file_path_str]
        if cached_mtime >= current_mtime:
            return cached_deps
    
    # Parse file and extract dependencies
    try:
        text = _getCachedFileContent(path)
        if text is None:
            text = path.read_text(encoding="utf-8")
            
        tree = ast.parse(text, filename=str(path))

        detected: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # grab only the top-level package
                    detected.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                detected.add(node.module.split(".")[0])

        result = sorted(detected)
        
        # Cache the result
        _AST_CACHE[file_path_str] = (current_mtime, result)
        
        # Limit cache size to prevent memory bloat
        moduleSettings = _loadModuleSettings()
        maxCacheSize = moduleSettings.get("performance", {}).get("ast_cache_size", 256)
        if len(_AST_CACHE) > maxCacheSize:
            # Remove oldest entries (simple LRU approximation)
            oldestEntries = sorted(_AST_CACHE.items(), key=lambda x: x[1][0])[:len(_AST_CACHE) - maxCacheSize + 1]
            for file_path, _ in oldestEntries:
                del _AST_CACHE[file_path]
        
        return result
        
    except (SyntaxError, OSError, UnicodeDecodeError) as e:
        # Cache empty result to avoid repeated parsing attempts
        _AST_CACHE[file_path_str] = (current_mtime, [])
        return []

@lru_cache(maxsize=512)
def isPythonPackage(moduleName: str) -> bool:
    """
    Check if a module is part of the Python standard library.
    Uses caching to avoid repeated expensive importlib operations.
    """
    if moduleName.startswith("_"):
        return True
    
    if moduleName in ["pkg_resources", "pathspec", "unicodedata"]: # "pkg_resources", is just here for temporary convenience
        spec = importlib.util.find_spec(moduleName)
        if spec:
            print(f"Spec for {moduleName}: {spec}")
        return True
    if moduleName in sys.builtin_module_names:
        return True
    
    try:
        spec = importlib.util.find_spec(moduleName)
        if not spec or not spec.origin:
            return False
        if spec.origin in {"built-in", "frozen"}:
            return True
            
        originPath = Path(spec.origin).resolve()
        stdlibPaths = _getStdlibPaths()
        stdlibPath = Path(stdlibPaths["stdlib"]).resolve()
        sitePackagesPath = Path(stdlibPaths.get("purelib", "")).resolve()
        
        if sitePackagesPath and str(originPath).startswith(str(sitePackagesPath)):
            return False
        return str(originPath).startswith(str(stdlibPath))
    except (ImportError, AttributeError, OSError):
        # If we can't determine, assume it's third-party
        return False

alwaysExclude = {".git", ".gitignore", ".gitmodules"}

def directoryMapper(basePath: Path) -> List[Path]:
    """
    Map all files in a directory tree, respecting .gitignore rules.
    Uses caching based on directory modification time.
    """
    basePath = basePath.resolve()
    base_path_str = str(basePath)
    
    try:
        current_mtime = basePath.stat().st_mtime
        # Also check .gitignore modification time
        gitignoreFile = basePath / ".gitignore"
        gitignore_mtime = gitignoreFile.stat().st_mtime if gitignoreFile.exists() else 0
        cache_key_mtime = max(current_mtime, gitignore_mtime)
    except (OSError, FileNotFoundError):
        cache_key_mtime = time.time()
    
    # Check cache first
    if base_path_str in _DIRECTORY_CACHE:
        cached_mtime, cached_paths = _DIRECTORY_CACHE[base_path_str]
        if cached_mtime >= cache_key_mtime:
            # Verify cached paths still exist (quick validation)
            if all(p.exists() for p in cached_paths[:5]):  # Sample check
                return cached_paths
    
    # Build file list
    if gitignoreFile.exists():
        patterns = _getCachedFileContent(gitignoreFile)
        if patterns is None:
            patterns = gitignoreFile.read_text().splitlines()
        else:
            patterns = patterns.splitlines()
        spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    else:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", [])
    
    paths: List[Path] = []
    for file in basePath.rglob("*"):
        rel = file.relative_to(basePath).as_posix()
        if any(part in alwaysExclude for part in file.parts):
            continue
        relSlash = rel + "/" if file.is_dir() else rel
        if spec.match_file(relSlash):
            continue
        paths.append(file)
    
    # Cache the result
    _DIRECTORY_CACHE[base_path_str] = (cache_key_mtime, paths)
    
    # Limit cache size
    if len(_DIRECTORY_CACHE) > 10:  # Keep cache small for directory listings
        oldestEntries = sorted(_DIRECTORY_CACHE.items(), key=lambda x: x[1][0])[:len(_DIRECTORY_CACHE) - 10 + 1]
        for dir_path, _ in oldestEntries:
            del _DIRECTORY_CACHE[dir_path]
    
    return paths

@overload
def settings() -> Dict[str, Any]:
    ...

@overload
def settings(settings: Dict[str, Any]) -> None:
    ...

def settings(settings: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    settingsPath = userProjectPath / ".pckgr" / "settings.json"
    if settings is None:
        if not settingsPath.exists():
            return {}
        with open(settingsPath, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        settingsPath.parent.mkdir(parents=True, exist_ok=True)
        with open(settingsPath, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        return None  # Explicit for clarity

def getGlobalSetting(key: str, default: Any = None) -> Any:
    """Get a global setting from module config, with fallback to project settings."""
    moduleSettings = _loadModuleSettings()
    globalSettings = moduleSettings.get("global", {})
    
    # Check module-level global settings first
    if key in globalSettings:
        value = globalSettings[key]
        # If it's author info and empty, try to get from git or prompt
        if key == "author" and not any(value.values()):
            return _getAuthorDetailsFromSettings()
        return value
    
    # Fallback to project-level settings
    projectSettings = settings()
    return projectSettings.get("global", {}).get(key, default)

def setGlobalSetting(key: str, value: Any) -> None:
    """Set a global setting in module config."""
    moduleSettings = _loadModuleSettings()
    globalSettings = moduleSettings.setdefault("global", {})
    globalSettings[key] = value
    
    # Save back to module settings
    config_path = Path(__file__).parent.parent / "config" / "module_settings.json"
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(moduleSettings, f, indent=4)
    
    # Invalidate cache
    global _MODULE_SETTINGS_CACHE, _MODULE_SETTINGS_MTIME
    _MODULE_SETTINGS_CACHE = None
    _MODULE_SETTINGS_MTIME = 0

def _getAuthorDetailsFromSettings() -> Dict[str, str]:
    """Get author details from various sources with priority order."""
    import subprocess
    
    # First try module settings
    moduleSettings = _loadModuleSettings()
    authorInfo = moduleSettings.get("global", {}).get("author", {})
    
    if authorInfo and all(authorInfo.values()):
        return authorInfo
    
    # Try git config
    def git_config_get(key: str) -> str:
        try:
            result = subprocess.run(
                ["git", "config", "--global", key],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return ""

    gitName = git_config_get("user.name")
    gitEmail = git_config_get("user.email") 
    gitGithub = git_config_get("user.github")
    
    # Use git values if available
    authorDetails = {
        "name": authorInfo.get("name") or gitName,
        "email": authorInfo.get("email") or gitEmail,
        "github": authorInfo.get("github") or gitGithub
    }
    
    # If still missing values, we'll need to prompt (handled by calling code)
    return authorDetails