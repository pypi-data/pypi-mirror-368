# UMF Python Parser

The Python Implementation of the [Universal Media Format](https://github.com/shmg-org/umf-specification).

## Example

```python
from umf import parse

source = """UMF Python Parser

[ Github ]
Author: IceBrick
Language: Python"""

metadata = parse(source)

print(metadata.get('Github', 'Author'))
```

## Installation

The package is available on [PyPI](https://pypi.org/project/umf.py/). You can install it using pip:

```bash
pip install umf.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
