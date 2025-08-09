# pyyaml-loaders

[PyPI package page](https://pypi.org/project/pyyaml-loaders/).

PyYAML loaders with enhanced functionalities.


## Description

### [`IgnoreLoader`](pyyaml_loaders/IgnoreLoader.py)

Ignore all constructors with tag `!`. Load YAML file as is.


### [`IncludeLoader`](pyyaml_loaders/IncludeLoader.py)

Tag: `!include`

Include values from other fields in the same YAML file, or from other file, while potentially replacing a subfield in the included field with a given value.

Syntax:
```yaml
!include [OTHER_FILE#]FIELD_TO_INCLUDE [SUBFIELD_TO_REPLACE:VALUE_TO_REPLACE_WITH]
```


## Installation

```bash
pip install pyyaml-loaders
```


## Usage

In preamble:

```python
from pyyaml_loaders import IncludeLoader, IgnoreLoader
```

When loading YAML file:
```python
with open(yaml_file, "r") as f:
    data = yaml.load(f, IncludeLoader)
```
(or `IgnoreLoader` instead of `IncludeLoader`)
