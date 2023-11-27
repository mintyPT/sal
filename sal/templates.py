# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/99_templates.ipynb.

# %% auto 0
__all__ = [
    "render",
    "JinjaTemplateRenderer",
    "TemplateLoader",
    "MissingTemplate",
    "InMemoryTemplateLoader",
    "Renderer",
]

# %% ../nbs/99_templates.ipynb 2
from .core import Data
from typing import Any, Optional
from jinja2 import Environment, BaseLoader, Template, StrictUndefined
from pathlib import Path

import abc

# %% ../nbs/99_templates.ipynb 4
def _get_env() -> Environment:
    return Environment(loader=BaseLoader(), undefined=StrictUndefined)


# %% ../nbs/99_templates.ipynb 6
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


# %% ../nbs/99_templates.ipynb 10
class JinjaTemplateRenderer:
    def render(self, template: str | None = None, **kwargs: Any) -> str:
        if template is None:
            raise RuntimeError("Missing template")
        return render(template, **kwargs)


# %% ../nbs/99_templates.ipynb 12
class TemplateLoader(abc.ABC):
    @abc.abstractmethod
    def get_template(self, name: str) -> str:
        """Separate method to allow an override to the template, before returning"""
        raise NotImplementedError


class MissingTemplate(Exception):
    def __init__(self, name: str):
        super().__init__(f"The template '{name}' is missing")
        self.name = name


# %% ../nbs/99_templates.ipynb 13
class InMemoryTemplateLoader(TemplateLoader):
    """
    Will keep a list of templates names + templates content
    """

    def __init__(
        self, *args: Any, templates: dict[str, str] | None = None, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.templates: dict[str, str] = templates or {}

    def get_template(self, name: str) -> str:
        if name in self.templates.keys():
            return self.templates[name]
        raise MissingTemplate(name)

    @classmethod
    def from_directory(cls, directory: str) -> "InMemoryTemplateLoader":
        path = Path(directory)
        glob = path.glob("*.jinja2")

        templates_raw = {}
        for p in glob:
            model_name = p.name.replace(".jinja2", "")
            with open(p, "r") as h:
                tpl = h.read()
            templates_raw[model_name] = tpl

        return cls(templates=templates_raw)


# %% ../nbs/99_templates.ipynb 16
class Renderer:
    # if no template is passed in, we use the DEFAULT_TEMPLATE
    DEFAULT_TEMPLATE = "{% for child in children %}{{ child | render }}{% endfor %}"

    def __init__(
        self,
        *,
        renderer: JinjaTemplateRenderer | None = None,
        repository: TemplateLoader | None = None,
        filters: dict | None = None,
    ):
        self.renderer = renderer
        self.repository = repository
        self.filters = filters or {}

    def render(self, data: Data, template: Optional[str] = None) -> str:
        if template is None:
            template = self.repository.get_template(data.name)

        ret = self.renderer.render(
            template=template,
            **data.attrs,
            filters={**self.filters, "render": self.render},
            node=data,
            children=data.children,
        )

        return ret

    def process(self, data: Data) -> str:
        return self.render(data)
