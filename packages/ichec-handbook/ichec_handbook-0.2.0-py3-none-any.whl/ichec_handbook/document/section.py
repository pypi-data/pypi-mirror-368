"""
Module representing document sections
"""

from pathlib import Path

from pydantic import BaseModel, field_serializer

from ..tags import Taggable
import ichec_handbook.content
from ..content import Content


class Section(BaseModel, Taggable):
    """
    A Section is the smallest piece of a document and
    can be associated with an individual file with
    document content.

    :param Path file: The path to the file with content
    :param Content content: A representation of the file's content
    """

    file: Path
    content: Content | None = None

    @field_serializer("file")
    def serialize_file(self, file: Path, _info):
        return str(file)

    def has_tag(self, tag: str) -> bool:
        """
        True if the provided tag is found in the file content

        :param str tag: The tag to search for
        """
        if not self.content:
            return False
        return self.content.has_tag(tag)

    @property
    def images(self) -> list[str]:
        if not self.content:
            return []
        return self.content.images


def load_content(root: Path, section: Section) -> Section:
    """
    Load the section's file content

    :param Path root: The absolute path to the top-level source dir
    :param Section section: The section to load the content for
    """
    return Section(
        file=section.file, content=ichec_handbook.content.load(root / section.file)
    )
