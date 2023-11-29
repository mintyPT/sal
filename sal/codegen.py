# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_codegen.ipynb.

# %% auto 0
__all__ = ['Sal']

# %% ../nbs/02_codegen.ipynb 2
import abc
from typing import Any

from .core import Data
from sal.templates import (
    Renderer,
)

# %% ../nbs/02_codegen.ipynb 11
class SalAction(abc.ABC):
    @property
    @abc.abstractmethod
    def name() -> str:
        pass

    @abc.abstractmethod
    def process_data(self, sal: "Sal", data: Data) -> str:
        pass

    def __str__(self):
        return f"action:{self.name}"


class ToFileAction(SalAction):
    name = "to-file"

    def process_data(self, sal: "Sal", data: Data) -> str:
        rendered = sal.renderer.render(data, template=Renderer.DEFAULT_TEMPLATE)
        to = data.attrs["to"]
        with open(to, "w") as h:
            h.write(rendered)
        return rendered


class ToStringAction(SalAction):
    name = "to-string"

    def process_data(self, sal: "Sal", data: Data) -> str:
        rendered = sal.renderer.render(data, template=Renderer.DEFAULT_TEMPLATE)
        return rendered


class WrapperAction(SalAction):
    name = "wrapper"

    def process_data(self, sal: "Sal", data: Data) -> str:
        return [sal.process(d) for d in data.children]

# %% ../nbs/02_codegen.ipynb 12
# TODO add support to inject more action into this
class Sal:
    def __init__(self, renderer: Renderer):
        self.renderer = renderer
        self.actions = [ToFileAction(), ToStringAction(), WrapperAction()]

    def pre_process_data(self, data: Data) -> Data:
        for d, _ in data:
            if d.name in self.action_names:
                continue
            # handle front matter

            if hasattr(self.renderer, "get_metadata_for_template"):
                # TODO rename this
                new_attributes = self.renderer.get_metadata_for_template(d.name, d)
                # update attributes
                d.attrs.update(new_attributes)
        return data

    def process_data(self, data: Data) -> str | Any:
        for action in self.actions:
            if data.name == action.name:
                return action.process_data(self, data)
        return self.renderer.process(data)

    def process(self, data: Data) -> str | Any:
        data = self.pre_process_data(data)
        return self.process_data(data)

    @property
    def action_names(self):
        return [action.name for action in self.actions]
