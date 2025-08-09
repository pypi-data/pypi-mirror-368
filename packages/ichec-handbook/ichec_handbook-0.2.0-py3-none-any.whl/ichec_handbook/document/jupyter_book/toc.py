"""
Module to handle a document's table of contents
"""

from pathlib import Path
import logging
import typing

from pydantic import BaseModel, field_serializer

from iccore.serialization import read_model_yaml, write_yaml

from ...document import toc, section
from ..jupyter_book import part as jb_part

from .part import Part

logger = logging.getLogger(__name__)


class TableOfContents(BaseModel):
    """
    A document's contents based on the Jupyter Book data
    model as per their yaml io format.

    :param str format: A format hint for Jupyter Book
    :param Path root: Path to the root file, such as frontmatter
    :param list[Part] parts: A list of document parts
    """

    format: str = "jb-book"
    root: Path
    parts: list[Part] = []

    @field_serializer("root")
    def serialize_root(self, root: Path, _info):
        return str(root)


def from_jupyterbook(jb_toc: TableOfContents) -> toc.TableOfContents:
    """
    Convert a Table of Contents in Jupyter Book format to the internal format
    """
    return toc.TableOfContents(
        format=jb_toc.format,
        root=section.Section(file=jb_toc.root),
        parts=[jb_part.from_jupyterbook(p) for p in jb_toc.parts],
    )


def to_jupyterbook(ic_toc: toc.TableOfContents) -> TableOfContents:
    """
    Convert a Table of Contents in the internal format to Jupyter Book format
    """

    return TableOfContents(
        format=ic_toc.format,
        root=ic_toc.root.file,
        parts=[jb_part.to_jupyterbook(p) for p in ic_toc.parts],
    )


def read(path: Path) -> TableOfContents:
    """
    Read the table of contents from a yaml file

    :param Path path: Path to the table of contents file
    """
    return typing.cast(TableOfContents, read_model_yaml(path, TableOfContents))


def write(path: Path, contents: TableOfContents) -> None:
    """
    Write the table of contents to file as yaml

    :param TableOfContents toc: The table of contents to write
    :param Path path: The path to the output file
    """
    write_yaml(path, contents.model_dump())
