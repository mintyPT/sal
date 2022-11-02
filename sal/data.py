# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_data.ipynb.

# %% auto 0
__all__ = ['WithChildrenMixin', 'Data', 'iter_data', 'MappedData', 'map_data']

# %% ../nbs/00_data.ipynb 3
from typing import Any
from collections import ChainMap
from textwrap import indent
from copy import deepcopy
from typing import Callable

# %% ../nbs/00_data.ipynb 5
class WithChildrenMixin:
    """Adds `parent`/`children`"""
    def __init__(self):
        self.parent = None
        self.children = []

    def __len__(self):
        return len(self.children)
    
    def __contains__(self, element):
        return element in self.children
            
    def add_child(self, child: "Data"):
        self.children.append(child)
        child.set_parent(self)
        return child
    
    def set_parent(self, parent: "Data"):
        self.parent = parent

# %% ../nbs/00_data.ipynb 6
class Data(WithChildrenMixin):
    """Data holder used during code generation. Logic is kept as separate functions"""
    def __init__(self, 
                 name:str, # name of this element
                 attrs: dict[str, Any] = None): # attributes
        
        self.name = name
        
        if attrs is None:
            attrs = {}
        self._attrs = attrs
        
        super().__init__()
    
    @property
    def attrs(self):
        if self.parent:
            return ChainMap(self._attrs, self.parent.attrs)
        return ChainMap(self._attrs)
            
    def clone(self):
        return deepcopy(self)
        
    def __eq__(self, a):
        same_name = self.name == a.name
        same_attrs = self.attrs == a.attrs
        same_children = self.children == a.children
        return same_name and same_attrs and same_children
    
    def __str__(self):
        
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

# %% ../nbs/00_data.ipynb 33
def iter_data(obj, level=0):
    """Simply yields parent and then children"""
    yield obj, level
    for child in obj.children:
        yield from iter_data(child, level=level+1)

# %% ../nbs/00_data.ipynb 39
class MappedData(WithChildrenMixin):
    """Data structure used to return results from the `map_data` function"""
    def __init__(self, value):
        self.value = value
        super().__init__()

# %% ../nbs/00_data.ipynb 40
def map_data(obj: Data, process: Callable, level=0) -> MappedData:
    """Maps over a `Data` inst returning `MappedData` instances"""
    child_results = [map_data(c, process, level=level+1) for c in obj.children]
    value = process(obj, level)
    data = MappedData(value)
    for c in child_results:
        data.add_child(c)
    return data
