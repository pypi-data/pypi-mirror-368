"""
Module to handle a document's table of contents
"""

from pathlib import Path
import typing
from typing import Any, Callable

from pydantic import BaseModel

from iccore.serialization import read_model_yaml, write_model_yaml

from ..document import part, section

from .part import Part
from .section import Section


class TableOfContents(BaseModel):
    """
    A document's contents based on the Jupyter Book data
    model as per their yaml io format.

    :param str jb_format: A format hint for Jupyter Book
    :param Section root: Path to the root file, such as frontmatter
    :param list[Part] parts: A list of document parts
    """

    format: str = "jb-book"
    root: Section
    parts: list[Part] = []

    @property
    def files(self) -> list[Path]:
        """
        Return paths to all content files in the document
        """
        files = []
        if self.root:
            files.append(self.root.file)
        for p in self.parts:
            files.extend(p.files)
        return files

    @property
    def images(self) -> list[str]:
        """
        Return paths to all images
        """

        images = []
        if self.root:
            images.extend(self.root.images)
        for p in self.parts:
            images.extend(p.images)
        return images


def read(path: Path) -> TableOfContents:
    """
    Read the table of contents from a yaml file

    :param Path path: Path to the table of contents file
    """
    return typing.cast(TableOfContents, read_model_yaml(path, TableOfContents))


def write(path: Path, toc: TableOfContents) -> None:
    """
    Write the table of contents to file as yaml

    :param TableOfContents toc: The table of contents to write
    :param Path path: The path to the output file
    """
    write_model_yaml(path, toc)


def load_content(root: Path, toc: TableOfContents) -> TableOfContents:
    """
    Load the file content for all elements of the table of content
    """
    return TableOfContents(
        root=section.load_content(root, toc.root),
        format=toc.format,
        parts=[part.load_content(root, p) for p in toc.parts],
    )


def filter_children(
    toc: TableOfContents, pred: Callable[[Any], bool]
) -> TableOfContents:
    """
    Return a table of contents with Parts matching the supplied tag
    """
    return TableOfContents(
        root=toc.root,
        format=toc.format,
        parts=[part.filter_children(p, pred) for p in toc.parts if pred(p)],
    )
