"""
Module for rendering media such as images and converting formats
"""

import logging
from pathlib import Path

from icplot import tex, mermaid
from icplot.tex import TexBuildSettings
from icplot.image_utils import svg_to_png, svg_to_pdf

logger = logging.getLogger(__name__)


def convert(
    source_dir: Path,
    output_dir: Path,
    build_dir: Path | None = None,
    extra_config: dict | None = None,
):
    """
    Convert supported media in the source directory to suitable formats
    and save them in the output directory. Optionally use a separate
    build directory for intermediate or temporary file generation.

    :param Path source_dir: The directory to search for source files
    :param Path output_dir: The directory to put converted files in
    :param Path build_dir: Optional directory for intermediate files
    """

    if not source_dir.exists():
        return

    if not build_dir:
        build_dir = output_dir

    logger.info("Start converting media")

    tex_config = TexBuildSettings(
        source=source_dir, build_dir=build_dir, output_dir=output_dir
    )
    tex.build(tex_config)

    svg_files = list(source_dir.glob("*.svg"))
    logger.info("Found %d svg files in %s", len(svg_files), source_dir)
    for svg_file in svg_files:
        svg_to_png(svg_file, output_dir / f"{svg_file.stem}.png")
        svg_to_pdf(svg_file, output_dir / f"{svg_file.stem}.pdf")

    mmd_files = list(source_dir.glob("*.mmd"))
    logger.info("Found %d mmd files in %s", len(mmd_files), source_dir)
    mermaid_config = None
    if extra_config and "mermaid" in extra_config:
        mermaid_config = Path(extra_config["mermaid"]).resolve()

    for mmd_file in mmd_files:
        mermaid.convert(mmd_file, output_dir, mermaid_config)

    logger.info("Finished converting media")
