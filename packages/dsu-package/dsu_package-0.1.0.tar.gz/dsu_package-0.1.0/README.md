# DSU Package

A Python implementation of the Disjoint Set Union (DSU) data structure, also known as Union-Find. This package provides efficient methods for union and find operations, commonly used in graph algorithms and connectivity problems.

## Features
- Efficient union and find operations
- Path compression
- Suitable for competitive programming and algorithmic tasks

## Installation
You can install the package using pip:
```bash
pip install .
```

## Usage
```python
from dsu_package.dsu import DSU

dsu = DSU(5)
dsu.union(0, 1)
dsu.union(1, 2)
print(dsu.find(2))  # Output: 0
```

## Testing
Run the unit tests using:
```bash
python -m unittest discover -s dsu_package/tests
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.
