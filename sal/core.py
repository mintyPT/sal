# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ["WithChildrenMixin", "Data", "MappedData", "map_data"]

# %% ../nbs/00_core.ipynb 2
from copy import deepcopy
from textwrap import indent
from collections import ChainMap
from typing import Callable, Any, Generator, Sequence, Optional

# %% ../nbs/00_core.ipynb 7
class WithChildrenMixin:
    """
    Adds `parent`/`children` functionality to a class.
    """

    def __init__(self) -> None:
        self.parent: "WithChildrenMixin" | None = None
        self.children: Sequence["WithChildrenMixin"] = []

    def __len__(self) -> int:
        return len(self.children)

    def __contains__(self, child: "WithChildrenMixin") -> bool:
        return child in self.children

    def append(self, child: "WithChildrenMixin") -> "WithChildrenMixin":
        """
        Add a child element to the children list and set its parent to self.
        """
        self.children.append(child)  # type: ignore[attr-defined]
        child.set_parent(self)
        return child

    def set_parent(self, parent: "WithChildrenMixin") -> None:
        """
        Set the parent element of self.
        """
        self.parent = parent

    def __iter__(self) -> Generator:
        def iter_data(obj: "WithChildrenMixin", level: int | None = 0) -> Generator:
            """Simply yields parent and then children"""
            yield obj, level
            for child in obj.children:
                yield from iter_data(child, level=(level or 0) + 1)

        return iter_data(self)


# %% ../nbs/00_core.ipynb 9
class Data(WithChildrenMixin):
    """
    Data holder used during code generation. Logic is kept as separate functions.
    """

    parent: Optional["Data"]
    children: Sequence["Data"]

    def __init__(
        self,
        name: str,  # Name of this element
        attrs: dict[str, Any] | None = None,  # Attributes for this element
    ) -> None:
        """
        Initialize Data object.

        """

        self.name = name

        if attrs is None:
            attrs = {}
        self._attrs = attrs

        super().__init__()

    @property
    def attrs(self) -> ChainMap:
        """
        Get the attributes for this element, merged with
        parent's attributes, if available.
        """
        if self.parent:
            return ChainMap(self._attrs, self.parent.attrs)
        return ChainMap(self._attrs)

    def clone(self) -> "Data":
        """
        Create a deep copy of this Data object.

        """
        return deepcopy(self)

    def __eq__(self, a: Any) -> bool:
        """
        Compare this Data object with another object for equality.

        """
        print("==")
        same_name: bool = self.name == a.name
        same_attrs: bool = self.attrs == a.attrs
        same_children: bool = self.children == a.children
        return same_name and same_attrs and same_children

    def __str__(self) -> str:
        """
        Get the string representation of this Data object.

        """
        is_self_closing = not self.children

        if self.children:
            children = "\n".join(map(str, self.children))
            children = children.strip()
            children = f"\n{children}\n"
            children = indent(children, "    ")

        if self.attrs:
            if is_self_closing:
                return f"<{self.name} {dict(self.attrs)} />"
            else:
                return f"<{self.name} {dict(self.attrs)}>{children}</{self.name}>"

        if is_self_closing:
            return f"<{self.name} />"
        else:
            return f"<{self.name}>{children}</{self.name}>"

    __repr__ = __str__


# %% ../nbs/00_core.ipynb 34
class MappedData(WithChildrenMixin):
    """Data structure used to return results from the `map_data` function"""

    def __init__(self, value: Any):
        self.value = value
        super().__init__()


# %% ../nbs/00_core.ipynb 35
def map_data(obj: Data, process: Callable, level: int | None = 0) -> MappedData:
    """Maps over a `Data` inst returning `MappedData` instances"""
    child_results = [map_data(c, process, level=(level or 0) + 1) for c in obj.children]
    value = process(obj, level)
    data = MappedData(value)
    for c in child_results:
        data.append(c)
    return data
