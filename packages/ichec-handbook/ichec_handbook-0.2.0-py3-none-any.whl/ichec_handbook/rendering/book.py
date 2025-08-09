"""
Module to support rendering of a book to disk given a book description
and a render context
"""

import logging
import shutil
import subprocess
from pathlib import Path

import iccore.filesystem as fs

from ..document.jupyter_book import toc as jb_toc
from ..document import toc, config
from ..rendering import document

from .context import RenderContext


logger = logging.getLogger(__name__)


def _copy_sources(
    contents: toc.TableOfContents, ctx: RenderContext, build: config.Build
):
    """
    Copy source files, filtered for the specific build, to the build
    directory.

    Also copy the filtered table of contents
    """

    build_dir = ctx.build_dir / build.name
    fs.copy_file(ctx.source_dir / "_config.yml", build_dir)

    jb_contents = jb_toc.to_jupyterbook(contents)
    jb_toc.write(build_dir / "_toc.yml", jb_contents)

    files_with_ext = [Path(f"{f}.md") for f in contents.files]
    fs.copy_files_relative(files_with_ext, ctx.source_dir, build_dir)
    return contents


def _jb_render(ctx: RenderContext, builder_args: str):
    args = ""
    if ctx.rebuild:
        args = "--all "

    cmd = f"jb build {args}{ctx.source_dir} --builder {builder_args}"

    with open(ctx.build_dir / "jb_logs.txt", "w", encoding="utf-8") as f:
        subprocess.run(cmd, shell=True, check=True, stdout=f, stderr=f)


def _render_html(doc_name: str, ctx: RenderContext):

    _jb_render(ctx, "html")
    fs.make_archive(
        ctx.build_dir / f"{doc_name}_html", "zip", ctx.build_dir / "html", rename=True
    )


def _render_pdf(doc_name: str, ctx: RenderContext):

    if not shutil.which("pdflatex"):
        logger.warning("pdflatex executable not found - skipping Latex rendering")
        return

    _jb_render(ctx, "pdflatex")
    shutil.move(ctx.build_dir / "latex/book.pdf", ctx.build_dir / f"{doc_name}.pdf")


def render(contents: toc.TableOfContents, ctx: RenderContext):
    """
    Render a book to disk for the given context
    :param TableOfContents contents: the content to render
    :param BuildContext ctx: the context (or settings) to render the book
    """

    contents = toc.load_content(ctx.source_dir, contents)
    document.render(
        contents, ctx, _copy_sources, {"pdf": _render_pdf, "html": _render_html}
    )
