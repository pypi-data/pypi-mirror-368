"""
A Part of a document, particularly a book. It is a collection
of Chapters.
"""

from pydantic import BaseModel

from ...document import part
from ..jupyter_book import chapter as jb_chapter

from .chapter import Chapter


class Part(BaseModel):
    """
    A Part is an element of a document, particularly a book,
    that is made of a collection of Chapters.

    :param str caption: A caption or title for the Part
    :param list[Chapter] chapters: A list of the Part's Chapters
    """

    caption: str = ""
    chapters: list[Chapter] = []


def from_jupyterbook(jb_part: Part) -> part.Part:
    """
    Convert a part in Jupyter Book format to the internal format
    """
    return part.Part(
        caption=jb_part.caption,
        chapters=[jb_chapter.from_jupyterbook(c) for c in jb_part.chapters],
    )


def to_jupyterbook(ic_part: part.Part) -> Part:
    """
    Convert a part in the internal format to Jupyter Book format
    """

    return Part(
        caption=ic_part.caption,
        chapters=[jb_chapter.to_jupyterbook(c) for c in ic_part.chapters],
    )
