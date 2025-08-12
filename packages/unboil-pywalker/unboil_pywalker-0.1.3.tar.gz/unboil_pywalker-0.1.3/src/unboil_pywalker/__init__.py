import importlib
from fnmatch import fnmatch
from pathlib import Path
from types import ModuleType

__all__ = [
    "import_modules",
    "walk_modules",
]

def import_modules(
    root: Path | str | ModuleType, 
    patterns: str | list[str] | None = None
):
    """
    Import all modules under the given root that match the given patterns.
    
    Args:
        root: Path, str, or ModuleType to search for modules.
        patterns: fnmatch pattern or list of patterns to filter module names.
    """
    for module_name in walk_modules(root, patterns):
        importlib.import_module(module_name)


def walk_modules(
    root: Path | str | ModuleType, 
    patterns: str | list[str] | None = None
):
    """
    Yield module names under the given root, optionally filtered by fnmatch patterns.
    
    Args:
        root: Path, str, or module to search for modules.
        patterns: fnmatch pattern or list of patterns to filter module names.
    Yields:
        str: Module names matching the patterns.
    """
    if isinstance(root, ModuleType):
        roots = [Path(item) for item in root.__path__]
    else:
        roots = [Path(root)]
    for root in roots:
        for path in root.rglob("*.py"):
            relative_path = path.relative_to(root.parent)
            nodes = [*relative_path.parts[:-1]]
            leaf = relative_path.stem
            if leaf != "__init__":
                nodes.append(leaf)
            module_name = ".".join(nodes)
            if patterns is None:
                yield module_name
            else:
                if isinstance(patterns, str):
                    patterns = [patterns]
                is_match = any(
                    fnmatch(module_name, pattern) 
                    for pattern in patterns
                )
                if is_match:
                    yield module_name