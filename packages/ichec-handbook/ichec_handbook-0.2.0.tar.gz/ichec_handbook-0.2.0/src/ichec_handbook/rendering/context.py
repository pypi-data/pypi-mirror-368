"""
Module for the rendering context
"""

from pathlib import Path

from pydantic import BaseModel

from ..document.config import Config


class RenderContext(BaseModel, frozen=True):
    """
    This captures the environment and configuration settings
    needed to render a document.
    """

    source_dir: Path
    build_dir: Path
    config: Config
    rebuild: bool = True

    @property
    def media_dir(self) -> Path:
        return self.source_dir / self.config.media_dir

    @property
    def media_build_dir(self) -> Path:
        return self.build_dir / "media"

    @property
    def conversion_dir(self) -> Path:
        return self.build_dir / "conversion"


def replace_dirs(ctx: RenderContext, new_dir: Path) -> RenderContext:
    return RenderContext(
        source_dir=new_dir,
        build_dir=new_dir / "_build",
        config=ctx.config,
        rebuild=ctx.rebuild,
    )
