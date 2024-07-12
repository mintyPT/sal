# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/99_templates.ipynb.

# %% auto 0
__all__ = ['render_to_remove']

# %% ../nbs/99_templates.ipynb 3
from pathlib import Path
from typing import Any, Optional, Union
from jinja2 import (
    Environment,
    BaseLoader,
    Template,
    StrictUndefined,
    TemplateNotFound,
    ChoiceLoader,
    DictLoader,
    FileSystemLoader,
)

from sal.core import Data
from sal.frontmatter import FrontMatter

# %% ../nbs/99_templates.ipynb 5
def _get_env() -> Environment:
    return Environment(loader=BaseLoader(), undefined=StrictUndefined)

# %% ../nbs/99_templates.ipynb 7
def render_to_remove(
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

# %% ../nbs/99_templates.ipynb 11
class TemplateRenderer:
    def render(self, template: Optional[str] = None, **kwargs: Any) -> str:
        if template is None:
            raise RuntimeError("Missing template")
        return render_to_remove(template, **kwargs)

# %% ../nbs/99_templates.ipynb 13
MissingTemplateException = TemplateNotFound


class TemplateLoader:
    def __init__(
        self,
        templates: Optional[dict[str, str]] = None,
        folders: Optional[list[Path]] = None,
    ):
        self.frontmatter_handler = FrontMatter()
        loaders: list[Union[DictLoader, FileSystemLoader]] = [
            DictLoader(templates or {})
        ]
        if folders:
            for folder in folders:
                loaders.append(FileSystemLoader(folder))
        self.loader = ChoiceLoader(loaders)

    def get_source(self, name: str, frontmatter: Optional[bool] = False) -> str:
        if not name.endswith(".jinja2"):
            name = name + ".jinja2"
        template, _, _ = self.loader.get_source(_get_env(), name)
        if not frontmatter:
            return self.frontmatter_handler.get_content(template)
        return self.frontmatter_handler.get_frontmatter_source(template)

    def get_frontmatter_source(self, name: str) -> str:
        return self.get_source(name, frontmatter=True)

    @classmethod
    def from_directories(cls, directories: list[Path]) -> "TemplateLoader":
        return cls(folders=directories)

# %% ../nbs/99_templates.ipynb 17
# TODO remove "any" typings
class Renderer:
    # if no template is passed in, we use the DEFAULT_TEMPLATE
    DEFAULT_TEMPLATE = "{% for child in children %}{{ child | render }}{% endfor %}"

    def __init__(
        self,
        *,
        renderer: TemplateRenderer,
        repository: TemplateLoader,
        filters: Optional[dict] = None
    ):
        self.renderer = renderer
        self.repository = repository
        self.filters = filters or {}

    def render(self, data: Data, template: Optional[str] = None) -> str:
        if template is None:
            template = self.repository.get_source(data.name)

        return self.renderer.render(
            template=template,
            **data.attrs,
            filters={**self.filters, "render": self.render},
            node=data,
            children=data.children,
        )

    def process(self, data: Data) -> str:
        return self.render(data)

    def get_source(self, *args: Any, **kwargs: Any) -> str:
        return self.repository.get_source(*args, **kwargs)

    def get_metadata_for_template(self, path: str, data: Data) -> dict:
        template = self.repository.get_frontmatter_source(path)

        rendered = self.render(data, template)

        ret: dict = self.repository.frontmatter_handler.parse(rendered)

        return ret
