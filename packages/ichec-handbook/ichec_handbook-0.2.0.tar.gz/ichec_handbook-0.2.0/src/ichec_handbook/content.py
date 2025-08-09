"""
Module supporting processing of file content
"""

from pathlib import Path
import logging

from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdformat.renderer import MDRenderer
from bs4 import BeautifulSoup
import yaml
import pydantic

from iccore.filesystem import read_file

from .hyperlink import Hyperlink

logging.getLogger("markdown_it").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def _md_it_wikify_link(self, tokens, idx, options, env):
    if "href" in tokens[idx].attrs:
        link = Hyperlink(link=tokens[idx].attrs["href"])
        tokens[idx].attrSet("href", link.wikify())
    return self.renderToken(tokens, idx, options, env)


def _wikify_link(token):
    if token.type != "link_open":
        return
    if "href" in token.attrs:
        link = Hyperlink(link=token.attrs["href"])
        token.attrSet("href", link.wikify())


def _visit_token(token, func):
    if token.children is not None:
        for child in token.children:
            _visit_token(child, func)
    else:
        func(token)


def wikify_links(parser, src: str) -> str:
    tokens = parser.parse(src)

    for token in tokens:
        _visit_token(token, _wikify_link)

    md_renderer = MDRenderer()
    options: dict = {}
    env: dict = {}
    return md_renderer.render(tokens, options, env)


def _parse_frontmatter(token, meta_key: str) -> list[str]:
    tags: list[str] = []
    if not token.content:
        return tags
    try:
        meta = yaml.safe_load(token.content)
    except Exception as e:
        logger.error("Failed to load frontmatter yaml")
        raise e
    if meta_key in meta and "tags" in meta[meta_key]:
        tags = meta[meta_key]["tags"]
    return tags


def _parse_fence(token) -> str | None:
    if token.info:
        if "}" in token.info:
            info_t, link = token.info.split("}")
            if info_t[1:] in ("image", "figure"):
                return link.strip()
    return None


def _render_html(parser, src: str) -> tuple[str, list[Hyperlink]]:
    html = parser.render(src)

    soup = BeautifulSoup(html, features="html.parser")
    links = soup.find_all("a", href=True)
    return (html, [Hyperlink(link=str(link)) for link in links])


class Content(pydantic.BaseModel):
    """
    This represents the content of a text file

    :param str src: The raw document source
    :param list[str] tags: Metadata tags in the document
    :param str html: The content as html
    :param list[Hyperlink]: Hyperlinks in the document
    """

    src: str = ""
    tags: list[str] = []
    html: str = ""
    links: list[Hyperlink] = []
    images: list[str] = []

    def has_tag(self, tag: str):
        return tag in self.tags


def load_markdown(path: Path, meta_key: str) -> Content:
    """
    Load and parse a markdown document from the provided file
    """

    src = read_file(path)

    parser = MarkdownIt().use(front_matter_plugin)
    tags = []
    images = []
    for t in parser.parse(src):
        if t.type == "front_matter":
            tags = _parse_frontmatter(t, meta_key)
        elif t.type == "fence":
            maybe_image = _parse_fence(t)
            if maybe_image:
                images.append(maybe_image)
        elif t.type == "inline":
            if not t.children:
                continue

            for c in t.children:
                if c.type == "image":
                    images.append(str(c.attrs["src"]))
    html, links = _render_html(parser, src)

    return Content(src=src, tags=tags, html=html, links=links, images=images)


def load(path: Path, meta_key: str = "ichec_handbook") -> Content:
    """
    Load and parse the document content from the provided file
    """

    for ext in ["md"]:
        candidate = Path(f"{path}.{ext}")
        if candidate.exists():
            if ext == "md":
                return load_markdown(candidate, meta_key)
    raise RuntimeError(f"No file with supported extension found: {path}")
