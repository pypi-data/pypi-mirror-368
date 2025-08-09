"""
Module for document configuration
"""

from pathlib import Path

from pydantic import BaseModel, field_serializer

from iccore.serialization import read_yaml, write_yaml

_DEFAULT_KEY = "ichec_handbook"


class Build(BaseModel, frozen=True):
    """
    A build configuration for the document

    :param str name: The name of the build
    :param set[str] outputs: Requested output formats: 'src', 'html', 'pdf'
    :param set[str] include_tags: Include only documents with these tags
    """

    name: str
    outputs: set[str] = set()
    include_tags: set[str] = set()
    exclude_tags: set[str] = set()


class Config(BaseModel, frozen=True):
    """
    The document configuation

    :param dict data: The raw data from the config file as dict
    :param str version: The document version
    :param str project_name: The project's name
    :param Path media_dir: Relative location of media content
    :param Path source_dir: Relative location of source files
    :param tuple[Build] builds: Build configurations
    """

    version: str = "0.0.0"
    project_name: str = "document"
    media_dir: Path = Path("src/media")
    source_dir: Path = Path("src")
    tools: dict = {}
    builds: list[Build] = []

    @field_serializer("media_dir")
    def serialize_media_dir(self, media_dir: Path, _info):
        return str(media_dir)

    @field_serializer("source_dir")
    def serialize_source_dir(self, source_dir: Path, _info):
        return str(source_dir)


def override_tools(config: Config, path: Path) -> Config:
    """
    Read the tools config from the given path and
    override the current config with its value. Useful
    for environment specific tool settings.
    """

    tools_config = read_yaml(path)
    return config.model_copy(update={"tools": tools_config})


def read(path: Path, key: str = _DEFAULT_KEY) -> Config:
    """
    Read the config from file. The Jupyter Book yaml format
    is assumed, with the config for this project under a
    specified key.


    :param Path path: The path to the config file
    :param str key: The key in the yaml to read the config from
    """
    config = read_yaml(path)
    return Config(**config[key])


def write(path: Path, config: dict, doc_config: Config, key: str = _DEFAULT_KEY):
    """
    Write the config to file, inserting the DocumentConfig under
    a specific key at the same time.

    :param Path path: The path to write to
    :param dict config: The full config in Jupyter Book format
    :param DocumentConfig doc_config: The config for this project
    :param str key: The key to insert the doc_config under
    """
    config[key] = doc_config.model_dump()
    write_yaml(path, config)
