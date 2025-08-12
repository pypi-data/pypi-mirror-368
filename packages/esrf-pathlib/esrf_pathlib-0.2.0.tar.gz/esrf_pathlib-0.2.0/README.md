# esrf-pathlib

`esrf-pathlib` is a drop-in replacement for Python’s built-in [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html),
extended with ESRF-specific attributes.

It detects and interprets known ESRF data directory structures and provides high-level access to proposal names, processed data locations, and more.

## Installation

```bash
pip install esrf-pathlib
```
## Getting Started

```python
from esrf_pathlib import ESRFPath

path = ESRFPath("/data/visitor/ma1234/id00/20250509/RAW_DATA/sample/sample_dataset")

print("Proposal:", path.proposal)
print("Processed results:", path.processed_data_path)
```

**Output:**
```bash
Proposal: ma1234
Processed results: /data/visitor/ma1234/id00/20250509/PROCESSED_DATA
```

The available attributes depend on the version of the ESRF data schema matched by the path.

## Documentation

https://esrf-pathlib.readthedocs.io/
