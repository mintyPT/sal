# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_codegen.ipynb.

# %% auto 0
__all__ = ['JinjaTemplateRenderer', 'TemplateLoader', 'MissingTemplate', 'InMemoryTemplateLoader', 'Renderer', 'SalBasic',
           'FrontMatterMixin', 'FrontMatterInMemoryTemplateLoader', 'Sal']

# %% ../nbs/02_codegen.ipynb 4
from .loaders import xml_to_data
from pathlib import Path
from .core import Data, iter_data, render, FrontMatter
from jinja2 import Environment, BaseLoader, Template
from typing import Optional, Any
import abc
from jinja2 import StrictUndefined
from textwrap import dedent
from yaml.parser import ParserError
from black import format_str, FileMode

# %% ../nbs/02_codegen.ipynb 13
class JinjaTemplateRenderer:
    def render(self, template=None, **kwargs) -> str:
        if template is None:
            raise RuntimeError("Missing template")
        return render(template, **kwargs)

# %% ../nbs/02_codegen.ipynb 15
class TemplateLoader(abc.ABC):
    @abc.abstractmethod
    def get_template(self, name: str) -> str:
        """Separate method to allow an override to the template, before returning"""
        raise NotImplementedError


class MissingTemplate(Exception):
    def __init__(self, name):
        super().__init__(f"The template {name} is missing")
        self.name = name

# %% ../nbs/02_codegen.ipynb 16
class InMemoryTemplateLoader(TemplateLoader):
    """
    Will keep a list of templates names + templates content
    """

    def __init__(self, *args, templates=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.templates = templates

    def get_template(self, name: str):
        if name in self.templates.keys():
            return self.templates[name]
        raise MissingTemplate(name)

    @classmethod
    def from_directory(cls, directory):
        path = Path(directory)
        glob = path.glob("*.jinja2")

        templates_raw = {}
        for p in glob:
            model_name = p.name.replace(".jinja2", "")
            with open(p, "r") as h:
                tpl = h.read()
            templates_raw[model_name] = tpl

        return cls(templates=templates_raw)

# %% ../nbs/02_codegen.ipynb 19
class Renderer:

    # if no template is passed in, we use the DEFAULT_TEMPLATE
    DEFAULT_TEMPLATE = "{% for child in children %}{{ child | render }}{% endfor %}"

    def __init__(
        self,
        *,
        renderer: JinjaTemplateRenderer = None,
        repository: TemplateLoader = None,
        filters=None
    ):
        self.renderer = renderer
        self.repository = repository
        self.filters = filters or {}

    def render(self, data: Data, template: Optional[str] = None) -> str:
        if template is None:
            template = self.repository.get_template(data.name)

        return self.renderer.render(
            template=template,
            **data.attrs,
            filters={**self.filters, "render": self.render},
            node=data,
            children=data.children,
        )

    def process(self, data: Data) -> str:
        return self.render(data)

# %% ../nbs/02_codegen.ipynb 23
class SalBasic:
    def __init__(self, renderer: Optional[Renderer] = None):
        self.renderer = renderer or Renderer()

    def pre_process_data(self, data: Data):
        return data

    def action_default(self, data: Data):
        return self.renderer.process(data)

    def action_to_file(self, data: Data):
        rendered = self.renderer.render(data, template=Renderer.DEFAULT_TEMPLATE)
        to = data.attrs["to"]
        with open(to, "w") as h:
            h.write(rendered)
        return rendered

    def action_black(self, data: Data):
        rendered = self.renderer.render(data, template=Renderer.DEFAULT_TEMPLATE)
        print(repr(rendered))
        return format_str(rendered, mode=FileMode())

    def process_data(self, data: Data):
        if data.name == "to-file":
            return self.action_to_file(data)
        if data.name == "black":
            return self.action_black(data)
        elif data.name == "wrapper":
            return [self.process(d) for d in data.children]
        else:
            return self.action_default(data)

    def process(self, data: Data):
        data = self.pre_process_data(data)
        return self.process_data(data)

# %% ../nbs/02_codegen.ipynb 43
class FrontMatterMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frontmatter_handler = FrontMatter()

    def get_template(self, data: Data, frontmatter=False):
        template = super().get_template(data)
        if not frontmatter:
            template = self.frontmatter_handler.get_content(template)
        else:
            template = self.frontmatter_handler.get_raw_frontmatter(template)
        return template


class FrontMatterInMemoryTemplateLoader(FrontMatterMixin, InMemoryTemplateLoader):
    pass

# %% ../nbs/02_codegen.ipynb 45
class Sal(SalBasic):
    def get_frontmatter_attributes_for_data(self, template: str, data: Data) -> dict:
        rendered = self.renderer.render(data, template)
        parsed = self.renderer.repository.frontmatter_handler.parse(rendered)
        return parsed

    def pre_process_data(self, data: Data):
        for d, _ in iter_data(data):

            if d.name in ["to-file", "black"]:
                continue

            # load template
            template = self.renderer.repository.get_template(d.name, frontmatter=True)
            # handle front matter
            new_attributes = self.get_frontmatter_attributes_for_data(template, d)

            # update attributes
            d.attrs.update(new_attributes)
        return data
