# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/99_templates.ipynb.

# %% auto 0
__all__ = []

# %% ../nbs/99_templates.ipynb 2
from .core import Data
from typing import Any, Optional
from jinja2 import Environment, BaseLoader, Template, StrictUndefined
from pathlib import Path
from .frontmatter import FrontMatter

import abc

# %% ../nbs/99_templates.ipynb 4
def _get_env() -> Environment:
    return Environment(loader=BaseLoader(), undefined=StrictUndefined)


# TODO start using a proper jinja template loader

# %% ../nbs/99_templates.ipynb 6
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

# %% ../nbs/99_templates.ipynb 10
class TemplateRenderer:
    def render(self, template: str | None = None, **kwargs: Any) -> str:
        if template is None:
            raise RuntimeError("Missing template")
        return render_to_remove(template, **kwargs)

# %% ../nbs/99_templates.ipynb 12
class TemplateLoader(abc.ABC):
    def __init__(self):
        self.frontmatter_handler = FrontMatter()

    # @abc.abstractmethod
    # def get_template(self, name: str) -> str:
    #     """Separate method to allow an override to the template, before returning"""
    #     raise NotImplementedError

    def _get_template(self, name: str, frontmatter: Optional[bool] = False) -> str:
        template = self.get_template_for_name(name)  # type: ignore[safe-super]
        if not frontmatter:
            return self.frontmatter_handler.get_content(template)
        return self.frontmatter_handler.get_raw_frontmatter(template)

    def get_template(self, name: str) -> str:
        return self._get_template(name, frontmatter=False)

    def get_raw_frontmatter(self, name: str) -> str:
        return self._get_template(name, frontmatter=True)

    @abc.abstractmethod
    def get_template_for_name(self, name: str) -> str:
        """TODO
        Use: raise MissingTemplateException(name)
        """
        raise NotImplementedError


# Rename this
class MissingTemplateException(Exception):
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

    def get_template_for_name(self, name: str) -> str:
        if name in self.templates.keys():
            return self.templates[name]
        raise MissingTemplateException(name)

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
# TODO remove "any" typings
class Renderer:
    # if no template is passed in, we use the DEFAULT_TEMPLATE
    DEFAULT_TEMPLATE = "{% for child in children %}{{ child | render }}{% endfor %}"

    def __init__(
        self,
        *,
        renderer: TemplateRenderer,
        repository: TemplateLoader,
        filters: dict | None = None
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

    def get_template(self, *args, **kwargs) -> Any:
        return self.repository.get_template(*args, **kwargs)

    def get_metadata_for_template(self, path: str, data: Data) -> dict:
        template = self.repository.get_raw_frontmatter(path)  # type: ignore[call-arg]
        rendered = self.render(data, template)
        return self.repository.frontmatter_handler.parse(
            rendered
        )  # type: ignore[attr-defined]
