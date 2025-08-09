"""
A Part of a document, particularly a book. It is a collection
of Chapters.
"""

from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel

from ..tags import Taggable
from ..document import chapter

from .chapter import Chapter


class Part(BaseModel, Taggable):
    """
    A Part is an element of a document, particularly a book,
    that is made of a collection of Chapters.

    :param str caption: A caption or title for the Part
    :param list[Chapter] chapters: A list of the Part's Chapters
    """

    caption: str = ""
    chapters: list[Chapter] = []

    @property
    def files(self) -> list[Path]:
        """
        Paths for all content files in the Path
        """
        return [p for c in self.chapters for p in c.files]

    @property
    def images(self) -> list[str]:
        images = []
        for c in self.chapters:
            images.extend(c.images)
        return images

    def has_tag(self, tag: str) -> bool:
        """
        True if any Chapter has the provided tag
        """
        return any(c.has_tag(tag) for c in self.chapters)


def filter_children(part: Part, pred: Callable[[Any], bool]) -> Part:
    """
    Return a Part with Chapters matching the predicate

    :param Part part: The part to filter
    :param Callable pred: The predicate to filter on
    """

    return Part(
        caption=part.caption,
        chapters=[chapter.filter_children(c, pred) for c in part.chapters if pred(c)],
    )


def load_content(root: Path, part: Part) -> Part:
    """
    Load content files in child Chapters
    """

    return Part(
        caption=part.caption,
        chapters=[chapter.load_content(root, c) for c in part.chapters],
    )
