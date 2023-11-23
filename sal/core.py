# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['WithChildrenMixin', 'Data', 'MappedData', 'map_data', 'render', 'FrontMatter', 'parse_arg', 'parse_attrs']

# %% ../nbs/00_core.ipynb 4
from typing import Any
from copy import deepcopy
from textwrap import indent
from collections import ChainMap
from typing import Callable, Optional
from jinja2 import Environment, BaseLoader, Template, StrictUndefined
from frontmatter.default_handlers import YAMLHandler
from frontmatter.util import u
from textwrap import dedent

# %% ../nbs/00_core.ipynb 9
class WithChildrenMixin:
    """
    Adds `parent`/`children` functionality to a class.
    """

    def __init__(self):
        self.parent = None
        self.children = []

    def __len__(self):
        return len(self.children)

    def __contains__(self, element):
        return element in self.children

    def append(self, child: "Data"):
        """
        Add a child element to the children list and set its parent to self.
        """
        self.children.append(child)
        child.set_parent(self)
        return child

    def set_parent(self, parent: "Data"):
        """
        Set the parent element of self.
        """
        self.parent = parent

    def __iter__(self):
        def iter_data(obj, level=0):
            """Simply yields parent and then children"""
            yield obj, level
            for child in obj.children:
                yield from iter_data(child, level=level + 1)

        return iter_data(self)

# %% ../nbs/00_core.ipynb 11
class Data(WithChildrenMixin):
    """
    Data holder used during code generation. Logic is kept as separate functions.
    """

    def __init__(
        self,
        name: str,  # Name of this element
        attrs: dict[str, Any] = None,  # Attributes for this element
    ):
        """
        Initialize Data object.

        """

        self.name = name

        if attrs is None:
            attrs = {}
        self._attrs = attrs

        super().__init__()

    @property
    def attrs(self):
        """
        Get the attributes for this element, merged with parent's attributes, if available.

        """
        if self.parent:
            return ChainMap(self._attrs, self.parent.attrs)
        return ChainMap(self._attrs)

    def clone(self):
        """
        Create a deep copy of this Data object.

        """
        return deepcopy(self)

    def __eq__(self, a):
        """
        Compare this Data object with another object for equality.

        """
        print("==")
        same_name = self.name == a.name
        same_attrs = self.attrs == a.attrs
        same_children = self.children == a.children
        return same_name and same_attrs and same_children

    def __str__(self):
        """
        Get the string representation of this Data object.

        """
        is_self_closing = not self.children

        if self.children:
            children = map(str, self.children)
            children = "\n".join(children)
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

# %% ../nbs/00_core.ipynb 36
class MappedData(WithChildrenMixin):
    """Data structure used to return results from the `map_data` function"""

    def __init__(self, value):
        self.value = value
        super().__init__()

# %% ../nbs/00_core.ipynb 37
def map_data(obj: Data, process: Callable, level=0) -> MappedData:
    """Maps over a `Data` inst returning `MappedData` instances"""
    child_results = [map_data(c, process, level=level + 1) for c in obj.children]
    value = process(obj, level)
    data = MappedData(value)
    for c in child_results:
        data.append(c)
    return data

# %% ../nbs/00_core.ipynb 44
def _get_env():
    return Environment(loader=BaseLoader(), undefined=StrictUndefined)

# %% ../nbs/00_core.ipynb 46
def render(
    template: str,  # template in string form
    filters: Optional[dict] = None,  # jinja filters
    **kwargs: Any,
) -> str:
    if not filters:
        filters = {}

    env = _get_env()
    env.filters.update(filters)

    jinja: Template = env.from_string(template)
    result: str = jinja.render(**kwargs)

    return result

# %% ../nbs/00_core.ipynb 51
class FrontMatter:
    def __init__(self, handler=None):
        if handler is None:
            handler = YAMLHandler()
        self.handler = handler

    def split(self, raw_content, *, encoding="utf-8"):
        raw_content = u(raw_content, encoding).strip()

        try:
            fm, content = self.handler.split(raw_content)
        except ValueError:
            return None, raw_content

        return fm, content

    def parse(self, raw_frontmatter, *, metadata=None):
        if metadata is None:
            metadata = {}

        try:
            raw_frontmatter = self.handler.load(raw_frontmatter)
        except Exception as e:
            msg = dedent(
                f"""
            ===
            There is an error with the following yaml (front matter)
            
            ```
            {raw_frontmatter}
            ```

            ===

            """
            )

            print(msg)
            raise e

        if isinstance(raw_frontmatter, dict):
            metadata.update(raw_frontmatter)

        return metadata

    def get_content(self, template):
        frontmatter, content = self.split(template)
        return content.strip()

    def get_raw_frontmatter(self, template):
        resp = self.split(template)
        frontmatter, content = resp
        if frontmatter:
            return frontmatter.strip()

# %% ../nbs/00_core.ipynb 53
import json

# %% ../nbs/00_core.ipynb 54
def parse_arg(arg):
    try:
        v = json.loads(arg)
    except json.JSONDecodeError:
        v = arg
    return v

# %% ../nbs/00_core.ipynb 57
def parse_attrs(attrs):
    for k, y in attrs.items():
        attrs[k] = parse_arg(y)
    return attrs
