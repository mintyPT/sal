# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_codegen.ipynb.

# %% auto 0
__all__ = ['Config', 'Sal']

# %% ../nbs/02_codegen.ipynb 2
import abc

from pydantic import BaseModel
from typing import Any, Callable
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

from .core import Data
from .loaders import xml_file_to_data
from sal.templates import (
    Renderer,
    TemplateLoader,
    TemplateRenderer,
    MissingTemplateException,
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


@dataclass
class WriteFileResult:
    to: str
    content: str


class ToFileAction(SalAction):
    name = "to-file"

    def process_data(self, sal: "Sal", data: Data) -> str:
        rendered = sal.renderer.render(data, template=Renderer.DEFAULT_TEMPLATE)

        if "to" not in data.attrs:
            raise RuntimeError(
                "To save to file you need to define the 'to' attribute with a filepath"
            )
        to = data.attrs["to"]

        return rendered, WriteFileResult(to=to, content=rendered)


class GroupAction(SalAction):
    name = "group"

    def process_data(self, sal: "Sal", data: Data) -> str:
        return [sal.process(d) for d in data.children], None

# %% ../nbs/02_codegen.ipynb 12
# TODO add support to inject more action into this
class Config(BaseModel):
    template_directories: list[Path]
    filters: dict[str, Callable] = {}


class Sal:
    def __init__(self, config: Config, renderer: Renderer):
        self.config = config
        self.renderer = renderer
        self.actions = [ToFileAction(), GroupAction()]  #  ToStringAction()
        self.action_results = []

    @property
    def action_names(self):
        return [action.name for action in self.actions]

    def pre_process_data(self, data: Data) -> Data:
        for d, _ in data:
            if d.name in self.action_names:
                continue
            new_attributes = self.renderer.get_metadata_for_template(d.name, d)
            d.attrs.update(new_attributes)
        return data

    def process_data(self, data: Data) -> str | Any:
        try:
            for action in self.actions:
                if data.name == action.name:
                    ret, action_result = action.process_data(self, data)
                    if action_result:
                        self.action_results.append(action_result)
                    return ret
            return self.renderer.process(data)
        except MissingTemplateException as e:
            path = Path(self.config.template_directories[0]) / f"{e.name}.jinja2"
            raise RuntimeError(
                dedent(
                    f"""
                The template `{e.name}` was not found. Here's a default template to 
                get you started:
                
                {self.renderer.DEFAULT_TEMPLATE}

                ---
                at: {path}
            """
                ).strip()
            )

    def process_xml_from_filename(self, file: str) -> str | Any:
        struct: Data = xml_file_to_data(file)
        return self.process(struct)

    def process_action_results(self) -> None:
        for action_result in self.action_results:
            if isinstance(action_result, WriteFileResult):
                print("writing to {result.to}: '{content}'")
                with open(action_result.to, "w") as h:
                    h.write(action_result.content)
            else:
                raise RuntimeError(f"Unsupported action {action_result}")

    def process(self, data: Data) -> str | Any:
        return self._process(data)

    # TODO support snapshots
    def _process(self, data: Data) -> str | Any:
        data = self.pre_process_data(data)
        result = self.process_data(data)
        self.process_action_results()
        return result

    # TODO support multiple template directories
    @classmethod
    def from_config(
        cls, template_directories: list[str], filters: dict[str, Callable] = {}
    ):
        config = Config(template_directories=template_directories, filters=filters)

        repository = TemplateLoader.from_directories(config.template_directories)

        template_renderer = Renderer(
            repository=repository, renderer=TemplateRenderer(), filters=config.filters
        )
        return cls(config, template_renderer)
