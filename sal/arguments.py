# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/99_arguments.ipynb.

# %% auto 0
__all__ = ["JsonType", "parse_arg", "parse_attrs"]

# %% ../nbs/99_arguments.ipynb 2
import json
from typing import Union

# %% ../nbs/99_arguments.ipynb 4
JsonType = Union[None, int, str, bool, list["JsonType"], dict[str, "JsonType"]]


def parse_arg(arg: str) -> JsonType:
    try:
        v: JsonType = json.loads(arg)
        return v
    except json.JSONDecodeError:
        return arg


# %% ../nbs/99_arguments.ipynb 7
def parse_attrs(attrs: dict) -> dict:
    for k, y in attrs.items():
        attrs[k] = parse_arg(y)
    return attrs
