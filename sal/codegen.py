# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_codegen.ipynb.

# %% auto 0
__all__ = ['SalBasic', 'FrontMatterMixin', 'FrontMatterInMemoryTemplateLoader', 'Sal']

# %% ../nbs/02_codegen.ipynb 2
from .loaders import xml_to_data
from pathlib import Path
from .core import Data, render, FrontMatter
from jinja2 import Environment, BaseLoader, Template
from typing import Optional, Any
import abc
from jinja2 import StrictUndefined
from textwrap import dedent
from yaml.parser import ParserError
from black import format_str, FileMode

# %% ../nbs/02_codegen.ipynb 11
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
        return format_str(rendered, mode=FileMode())

    def process_data(self, data: Data):
        if data.name == "to-file":
            return self.action_to_file(data)
        elif data.name == "black":
            return self.action_black(data)
        elif data.name == "wrapper":
            return [self.process(d) for d in data.children]
        else:
            return self.action_default(data)

    def process(self, data: Data):
        data = self.pre_process_data(data)
        return self.process_data(data)

# %% ../nbs/02_codegen.ipynb 31
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

# %% ../nbs/02_codegen.ipynb 33
class Sal(SalBasic):
    def get_frontmatter_attributes_for_data(self, template: str, data: Data) -> dict:
        rendered = self.renderer.render(data, template)
        parsed = self.renderer.repository.frontmatter_handler.parse(rendered)
        return parsed

    def pre_process_data(self, data: Data):
        for d, _ in data:

            if d.name in ["to-file", "black", "wrapper"]:
                continue

            # load template
            template = self.renderer.repository.get_template(d.name, frontmatter=True)
            # handle front matter
            new_attributes = self.get_frontmatter_attributes_for_data(template, d)

            # update attributes
            d.attrs.update(new_attributes)
        return data
