from pathlib import Path

from pydantic import BaseModel, model_serializer

from ...document import section, chapter
from ..jupyter_book import section as jb_section

from .section import Section


class Chapter(BaseModel):
    """
    Class representing a document chapter following the Jupyter Book
    representation. It can be composed of document Sections.

    The Chapter can have an optional root or base section and
    can in addition be broken down into a collection of Sections.

    :param Path file: The chapter can have a 'root' section here
    :param list[Section] sections: A list of Sections in the Chapter
    """

    file: Path | None = None
    sections: list[Section] = []

    @model_serializer
    def serialize_model(self):
        ret = {}
        if self.file:
            ret["file"] = str(self.file)
        if self.sections:
            ret["sections"] = self.sections
        return ret


def from_jupyterbook(jb_chapter: Chapter) -> chapter.Chapter:
    """
    Convert a chapter in Jupyter Book format to the internal format
    """

    base = None
    if jb_chapter.file:
        base = section.Section(file=jb_chapter.file)

    return chapter.Chapter(
        base=base,
        sections=[jb_section.from_jupyterbook(s) for s in jb_chapter.sections],
    )


def to_jupyterbook(ic_chapter: chapter.Chapter) -> Chapter:
    """
    Convert a chapter in the internal format to Jupyter Book format
    """

    file = None
    if ic_chapter.base:
        file = ic_chapter.base.file

    return Chapter(
        file=file,
        sections=[jb_section.to_jupyterbook(s) for s in ic_chapter.sections],
    )
