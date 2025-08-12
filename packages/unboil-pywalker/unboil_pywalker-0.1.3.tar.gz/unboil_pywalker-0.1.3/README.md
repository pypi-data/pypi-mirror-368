# Usage

## Importing all modules


You can import all modules under a given root directory, package, or module:

```python
import mypackage  # your package or module
from pywalker import import_modules
import_modules(mypackage)
```

## Filtering with patterns


You can filter which modules are imported using an fnmatch pattern (or list of patterns):


```python
import mypackage
import_modules(mypackage, patterns='utils*')
import_modules(mypackage, patterns=['core*', 'utils*'])
```

## Walking modules without importing

To just get the module names (without importing them):


```python
import mypackage
from pywalker import walk_modules
for name in walk_modules(mypackage, patterns='*test*'):
    print(name)
```

## Pattern argument

The `patterns` argument uses Unix shell-style wildcards (see Python's `fnmatch`):

- `*` matches everything
- `?` matches any single character
- `[seq]` matches any character in seq
- `[!seq]` matches any character not in seq

Examples:

- `'core*'` matches modules starting with `core`
- `'*test*'` matches modules containing `test`
