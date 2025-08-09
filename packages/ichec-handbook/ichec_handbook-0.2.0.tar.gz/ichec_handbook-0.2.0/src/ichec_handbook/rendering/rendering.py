"""
Module for document rendering functions
"""

import logging
from pathlib import Path

from ..document import toc
from ..document.jupyter_book import toc as jb_toc
import ichec_handbook.document.config
from ..rendering import book, RenderContext

logger = logging.getLogger(__name__)


def render_book(
    source_dir: Path,
    build_dir: Path,
    config_path: Path,
    rebuild: bool,
    tools_config: Path | None,
):
    """
    Render a book - i.e. given sources and a config path build html, pdf or source
    archives of the book content.
    """

    logger.info("Loading config from %s", config_path)
    config = ichec_handbook.document.config.read(config_path)
    if tools_config:
        config = ichec_handbook.document.config.override_tools(config, tools_config)

    toc_path = source_dir / "_toc.yml"
    logger.info("Reading toc from %s", toc_path)
    contents = toc.load_content(
        source_dir, jb_toc.from_jupyterbook(jb_toc.read(toc_path))
    )

    ctx = RenderContext(
        source_dir=source_dir,
        build_dir=build_dir,
        config=config,
        rebuild=rebuild,
    )
    book.render(contents, ctx)
