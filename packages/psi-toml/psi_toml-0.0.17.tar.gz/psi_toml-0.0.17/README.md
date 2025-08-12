# psi_toml

A very lite implementation of a toml parser, reader, and writer

It is not a **1.0.0-compliant** [TOML](https://toml.io/) library, nor is it intended to be.

It can parse basic toml files to a dict, and write a dict to a toml file using the *load* and *dump* methods.

## Usage

```python
from psi_toml import toml as toml
    result = toml.load(f_toml)
```

```python
    toml.dump(data, f_toml)
```

```python
    toml.parse(strings)
```

where *f_toml* is the handle to the toml file, *data* is a python dict and *strings* is a list of strings representing key value pairs. E.g.

```python
    nl = '\n'
    strings = [
        'a = 1',
        'b = -1',
        'c = .5',
        'd = abc',
        'e = 3.14',
        'f = "1.414"',
        'g = true',
        'h = "false"',
        (f'i = [{nl}'
            f'"a",{nl}'
            f'"b",{nl}'
            f'"c",{nl}'
            f'"d",{nl}'
            f']'),
        (f'j = {{{nl}'
            f'"a": 1,{nl}'
            f'"b": 2,{nl}'
            f'"c": 3,{nl}'
            f'"d": 4,{nl}'
            f'}}')
    result = toml.parse(strings)

```

## Installation

If you are using [Poetry](https://poetry.eustace.io),
add `psi_toml` to your `pyproject.toml` file by using:

```bash
poetry add psi_toml
```

If not, you can use `pip`:

```bash
pip install psi_toml
