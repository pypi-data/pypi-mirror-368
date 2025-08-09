"""
Module to handle document chapters
"""

from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel

from ..tags import Taggable
from ..document import section
from .section import Section


class Chapter(BaseModel, Taggable):
    """
    Class representing a document chapter following the Jupyter Book
    representation. It can be composed of document Sections.

    The Chapter can have an optional root or base section and
    can in addition be broken down into a collection of Sections.

    :param Section base: An optional root or base section
    :param list[Section] sections: A list of Sections in the Chapter
    """

    base: Section | None = None
    sections: list[Section] = []

    @property
    def files(self) -> list[Path]:
        """
        A list of file paths for all sections
        """
        files = []
        if self.base:
            files.append(self.base.file)
        files.extend([s.file for s in self.sections])
        return files

    @property
    def images(self) -> list[str]:
        """
        A list of all images for all sections
        """
        images = []
        if self.base:
            images.extend(self.base.images)
        for s in self.sections:
            images.extend(s.images)
        return images

    def has_tag(self, tag: str) -> bool:
        """
        True if any Section has the provided tag
        """
        if self.base and self.base.has_tag(tag):
            return True
        return any(s.has_tag(tag) for s in self.sections)


def filter_children(chapter: Chapter, pred: Callable[[Any], bool]) -> Chapter:
    """
    Return a Chapter with only Sections matching the predicate.

    :param Chapter chapter: The chapter to filter
    :param pred Callable: The predicate to filter on
    """

    base: Section | None = None
    if chapter.base and pred(chapter.base):
        base = chapter.base

    return Chapter(
        base=base,
        sections=[s for s in chapter.sections if pred(s)],
    )


def load_content(root: Path, chapter: Chapter) -> Chapter:
    """
    Load file content into the Chapter

    :param Path root: The absolute path to the top-level source dir
    :param Chapter chapter: The Chapter to load content for
    """

    base: Section | None = None
    if chapter.base:
        base = section.load_content(root, chapter.base)

    return Chapter(
        base=base,
        sections=[section.load_content(root, s) for s in chapter.sections],
    )
