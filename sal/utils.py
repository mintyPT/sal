# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/99_utils.ipynb.

# %% auto 0
__all__ = ['files', 'is_notebook']

# %% ../nbs/99_utils.ipynb 2
from pathlib import Path
from typing import Generator
from IPython import get_ipython
from contextlib import contextmanager

# %% ../nbs/99_utils.ipynb 4
@contextmanager
def files(content: dict[str, str]) -> Generator:
    """Setup files with content. No override if file already exists."""
    try:
        for filepath, text in content.items():
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                raise RuntimeError("This file already exists {path}")
            path.write_text(text)

        yield

    finally:
        for filepath in content.keys():
            path = Path(filepath)
            path.unlink()

# %% ../nbs/99_utils.ipynb 7
def is_notebook() -> bool:
    """Check if we are running code in a notebook or in a shell"""
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell" or shell == "CaptureShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter
