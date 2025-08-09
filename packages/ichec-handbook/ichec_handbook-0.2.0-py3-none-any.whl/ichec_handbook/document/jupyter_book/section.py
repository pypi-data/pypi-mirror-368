from pathlib import Path

from pydantic import BaseModel, field_serializer

from ...document import section


class Section(BaseModel):
    """
    A Section is the smallest piece of a document and
    can be associated with an individual file with
    document content.

    :param Path file: The path to the file with content
    """

    file: Path

    @field_serializer("file")
    def serialize_file(self, file: Path, _info):
        return str(file)


def from_jupyterbook(jb_section: Section) -> section.Section:
    return section.Section(file=jb_section.file)


def to_jupyterbook(ic_section: section.Section) -> Section:
    return Section(file=ic_section.file)
